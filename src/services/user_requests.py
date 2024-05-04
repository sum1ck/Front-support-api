import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from src.models.request import Request, RequestCategory, Category, RequestLikes
from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



async def get_requests(location: Optional[str] = None, categories: Optional[str] = None, db: Session = Depends(get_db)):
    query = (
        db.query(Request, Category.id, Category.name)
        .outerjoin(RequestCategory, Request.id == RequestCategory.request_id)
        .outerjoin(Category, Category.id == RequestCategory.category_id)
        .group_by(Request.id, Category.id, Category.name)
        .order_by(desc(Request.creation_time))
    )
    if location:
        query = query.filter(Request.location == location)
    if categories:
        category_names = categories.split("|")
        query = query.filter(Category.name.in_(category_names))

    requests_with_categories = query.all()

    requests_dict = {}
    for request, category_id, category_name in requests_with_categories:
        if request.id not in requests_dict:
            user = db.query(User).filter(User.id == request.user_id).first()
            user_data = {
                "username": user.username,
                "phoneNumber": user.phone_number,
                "email": user.email,
                "role": user.role
            }
            all_categories_query = (
                db.query(Category.id, Category.name)
                .join(RequestCategory, Category.id == RequestCategory.category_id)
                .filter(RequestCategory.request_id == request.id)
            )
            all_categories = all_categories_query.all()
            categories_list = [{"id": cat_id, "name": cat_name} for cat_id, cat_name in all_categories]

            requests_dict[request.id] = {
                "user": user_data,
                "requestId": request.id,
                "description": request.description,
                "location": request.location,
                "categories": categories_list  # Додати всі категорії до реквесту
            }

    formatted_requests = list(requests_dict.values())
    total_requests = len(formatted_requests)

    return total_requests, formatted_requests


async def get_user_requests(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=["HS384"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        requests_with_categories = (
            db.query(Request, func.count(RequestLikes.request_id), Category.id, Category.name)
            .outerjoin(RequestLikes, Request.id == RequestLikes.request_id)
            .outerjoin(RequestCategory, Request.id == RequestCategory.request_id)
            .outerjoin(Category, Category.id == RequestCategory.category_id)
            .filter(Request.user_id == user.id if user.role == "ROLE_AUTHOR" else RequestLikes.user_id == user.id)
            .group_by(Request.id, Category.id, Category.name)
            .order_by(desc(Request.creation_time))
            .all()
        )

        requests_dict = {}
        for request, like_count, category_id, category_name in requests_with_categories:
            if request.id not in requests_dict:
                requests_dict[request.id] = {
                    "requestId": request.id,
                    "description": request.description,
                    "location": request.location,
                    "user_id": request.user_id,
                    "like_count": like_count,
                    "categories": []
                }
            if category_id:
                requests_dict[request.id]["categories"].append({"id": category_id, "name": category_name})

        formatted_requests = list(requests_dict.values())

        total_requests = len(formatted_requests)

        return formatted_requests, total_requests
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")









