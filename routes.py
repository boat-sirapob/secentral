from fastapi import APIRouter, Depends, Request, Body, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from auth import login_manager
from app import app, user_manager, challenge_manager, post_manager
from database import save, PostManager

import markdown
import shutil
from pathlib import Path
import pyston
import random, string
import re

main = APIRouter()
templates = Jinja2Templates(directory="templates")

# handle private endpoints
def get_context(request: Request, user=Depends(login_manager.optional)):
    context = {"request": request}
    if user is not None:
        context["logged_in"] = True
        context["user"] = user
    return context

# views
@main.get("/", response_class=HTMLResponse)
@main.get("/home", response_class=HTMLResponse)
def home(request: Request, user=Depends(login_manager.optional)):
    return templates.TemplateResponse("index.html", get_context(request, user))

# challenges
@main.get("/challenges", response_class=HTMLResponse)
def challenges_select(request: Request, user=Depends(login_manager.optional)):
    return templates.TemplateResponse("challenges.html", get_context(request, user))

@main.get("/challenges/{chall_id}", response_class=HTMLResponse)
def challenges_main(chall_id: str, request: Request, user=Depends(login_manager.optional)):
    challenge = challenge_manager.get_challenge_from_id(
        chall_id,
        details=["_id", "code", "title", "instructions", "lab", "difficulty"]
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    challenge["instructions"] = markdown.markdown(challenge["instructions"], extensions=["fenced_code", "tables"])
    
    context = get_context(request, user)
    context["challenge"] = challenge
    context["score"] = challenge_manager.get_score(challenge["difficulty"])
    
    return templates.TemplateResponse("runner.html", context)

# forum
@main.get("/forum", response_class=HTMLResponse)
def forum(request: Request, page: int = 1, sort_by: str = "recent", search: str | None = None, user=Depends(login_manager.optional)):
    posts = post_manager.get_page(page, sort_by, search)

    context = get_context(request, user)
    post_dicts = [p.get_dict() for p in posts]
    for p in post_dicts:
        p["author_name"] = user_manager.get_user_from_uuid(p["author_uuid"]).name

    context["posts"] = post_dicts
    context["per_page"] = PostManager.POSTS_PER_PAGE
    context["page"] = page
    context["sort_by"] = sort_by
    context["search"] = search

    return templates.TemplateResponse("forum.html", context)

@main.get("/forum/post/{post_id}", response_class=HTMLResponse)
def view_post(request: Request, post_id: str, user=Depends(login_manager.optional)):
    post = post_manager.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    context = get_context(request, user)
    context["post"] = post.get_dict()
    context["get_user"] = user_manager.get_user_from_uuid
    
    return templates.TemplateResponse("post.html", context)

@main.post("/forum/create_post")
def create_post(request: Request, title: str = Form(...), content: str = Form(...), user=Depends(login_manager.optional)):
    if user is None:
        return RedirectResponse("/login", status_code=302)

    author_uuid = user.uuid
    post = post_manager.create_post(title, content, author_uuid)
    
    user.add_post(post)
    save()
    
    return RedirectResponse(f"/forum/post/{post.post_id}", status_code=302)

@main.post("/forum/post/{post_id}/new_comment", response_class=HTMLResponse)
def create_new_comment(request: Request, post_id: str, comment_body: str = Form(...), user=Depends(login_manager.optional)):
    if user is None:
        return RedirectResponse("/login", status_code=302)
    
    comment = post_manager.add_comment(post_id, user.uuid, comment_body)
    
    user.add_comment(comment)
    save()
    
    return RedirectResponse(f"/forum/post/{post_id}", status_code=302)

@main.post("/forum/post/{post_id}/edit_comment", response_class=HTMLResponse)
def edit_comment(request: Request, post_id: str, new_content: str = Form(...), comment_id: str = Form(...), user=Depends(login_manager.optional)):
    comment = post_manager.get_comment_by_id(post_id, comment_id)
    
    if user is None or user.uuid != comment.author_uuid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    comment.edit_comment(new_content)
    save()
    
    return RedirectResponse(f"/forum/post/{post_id}", status_code=302)

@main.post("/forum/post/{post_id}/delete_comment", response_class=HTMLResponse)
def delete_comment(request: Request, post_id: str, comment_id: str = Form(...), user=Depends(login_manager.optional)):
    comment = post_manager.get_comment_by_id(post_id, comment_id)
    
    if user is None or user.uuid != comment.author_uuid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    post_manager.delete_comment(post_id, comment_id)
    save()
    
    return RedirectResponse(f"/forum/post/{post_id}", status_code=302)

# profile
def get_luminescence(color_code):
    # handle short format
    if len(color_code) == 4:
        color_code = '#' + ''.join([char * 2 for char in color_code[1:]])

    r = int(color_code[1:3], 16) / 255.0
    g = int(color_code[3:5], 16) / 255.0
    b = int(color_code[5:7], 16) / 255.0

    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    return luminance

@main.get("/profile/{user_id}", response_class=HTMLResponse)
def profile(request: Request, user_id: str, user=Depends(login_manager.optional)):    
    
    profile_user = user_manager.get_user_from_uuid(user_id)
    
    if profile_user is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    context = get_context(request, user)
    context["profile_user"] = profile_user
    context["get_luminescence"] = get_luminescence
    
    return templates.TemplateResponse("profile.html", context)

@main.get("/profile/get-photo/{user_id}")
async def get_photo(request: Request, user_id: str, user=Depends(login_manager.optional)):
    
    profile_user = user_manager.get_user_from_uuid(user_id)
    
    if profile_user is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    file_path = profile_user.get_profile_pic_path()
    
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate"
    }
    
    if file_path == "":
        return FileResponse("static/assets/placeholder_profile.png", headers=headers)
    
    return FileResponse(file_path, headers=headers)

@main.post("/profile/upload-photo/{user_id}")
async def upload_photo(request: Request, user_id: str, file: UploadFile = File(...), user=Depends(login_manager.optional)):
    if user is None or user.uuid != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    # get the file size (in bytes)
    file.file.seek(0, 2)
    file_size = file.file.tell()

    # move the cursor back to the beginning
    await file.seek(0)

    if file_size > 2 * 1024 * 1024:
        # more than 2 MB
        raise HTTPException(status_code=400, detail="File too large")

    # check the content type
    content_type = file.content_type
    if content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_path = f"static/uploads/{str(user.uuid)}{Path(file.filename).suffix}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.set_profile_pic_path(file_path)
    save()

    return RedirectResponse(f"/profile/{user_id}", status_code=302)

@main.post("/profile/change-theme/{user_id}")
async def change_theme(request: Request, user_id: str, color: str = Form(...), user=Depends(login_manager.optional)):
    if user is None or user.uuid != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    HEX_COLOR_REGEX = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    pattern = re.compile(HEX_COLOR_REGEX)
    
    if re.search(pattern, color) is False:
        return HTTPException(status_code=400, detail="Invalid color code")
    
    user.set_profile_color(color)
    save()
    
    return RedirectResponse(f"/profile/{user_id}", status_code=302)

@app.exception_handler(404)
def not_found(request: Request, exc: HTTPException, user=Depends(login_manager.optional)):
    context = get_context(request, user)
    return templates.TemplateResponse("404.html", context, status_code=404)

# internal API
@main.get("/api/challenges/{difficulty}")
def get_challenges(difficulty: str, user=Depends(login_manager.optional)):
    details = ["_id", "title", "difficulty"]
    
    if not difficulty.isnumeric():
        raise HTTPException(status_code=400, detail="Bad request")
    
    challenges = challenge_manager.get_challenges_with_difficulty(int(difficulty))
    challenge_dicts = [c.__dict__ for c in challenges]
    result = [{key: c[key] for key in details} for c in challenge_dicts]
    
    for challenge in result:
        score = challenge_manager.get_score(challenge["difficulty"])        
        challenge["score"] = score
        challenge["completed"] = user.get_challenge_completed(challenge["_id"]) if user else False
    
    return result

# using Piston API
async def execute_code(code, tests=None):
    try:
        client = pyston.PystonClient()
        
        print(code)
        
        code_with_test_runner = code + "\n" + """
class Test:
\t@ staticmethod
\tdef assert_equals(test, expected):
\t\tif test == expected:
\t\t\tprint(f"Test Passed: {test} == {expected}")
\t\telse:
\t\t\tprint(f"Test Failed: expected {expected}, got {test}")
""" + tests if tests is not None else ""

        output = await client.execute("python", files=[pyston.File(code_with_test_runner)])
        
        return output
    except Exception as e:
        return str(e)
    
async def execute_code_for_submit(code, tests):
    # random variable name to prevent cheating
    num_tests = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    passed_tests = "".join(random.choice(string.ascii_lowercase) for _ in range(10))

    try:
        client = pyston.PystonClient()

        test_runner = code + "\n" + f"""
class Test:
\t{num_tests} = 0
\t{passed_tests} = 0
\t@staticmethod
\tdef assert_equals(test, expected):
\t\tTest.{num_tests} += 1
\t\tif test == expected:
\t\t\tTest.{passed_tests} += 1
""" + tests + "\n" + f"print(Test.{num_tests}, Test.{passed_tests})"

        output = await client.execute("python", files=[pyston.File(test_runner)])

        print(output)

        split_output = output.run_stage.output.split()
        
        if len(split_output) != 2:
            return
        
        num_tests_result, passed_tests_result = split_output[-2:]
        
        return int(num_tests_result), int(passed_tests_result)
    except Exception as e:
        print(str(e))
    
@main.post("/api/challenges/run/{challenge_id}")
async def compile_runner(challenge_id: str, code: str = Body(""), user=Depends(login_manager.optional)):
    if user is None:
        return HTTPException(status_code=403, detail="User not logged in")
    
    challenge = challenge_manager.get_challenge_from_id(challenge_id, details=["lab"])
    if not challenge:
        return HTTPException(status_code=400, detail="Challenge not found")
    
    tests = challenge["lab"]
    
    output = await execute_code(code, tests)
    
    print(output)
    
    return output

@main.post("/api/challenges/submit/{challenge_id}")
async def submit_runner(challenge_id: str, code: str = Body(""), user=Depends(login_manager.optional)):
    if user is None:
        return HTTPException(status_code=403, detail="User not logged in")
    
    challenge = challenge_manager.get_challenge_from_id(challenge_id, details=["difficulty", "lab"])
    if not challenge:
        return HTTPException(status_code=400, detail="Challenge not found")
    
    tests = challenge["lab"]
    
    output = await execute_code_for_submit(code, tests)
    
    print(output)
    
    if output:
        num_tests, passed_tests = output
        score = challenge_manager.get_score(challenge["difficulty"])
        user_score = score * passed_tests/num_tests
        rounded_user_score = round(user_score, -1)
        user.add_completed_challenge(challenge_id, rounded_user_score)
    
        return rounded_user_score
    else:
        user.add_completed_challenge(challenge_id, 0)
        
    return output
    