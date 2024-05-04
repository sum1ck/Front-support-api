import secrets
import string
from email.utils import make_msgid

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from src.dto.user import UserModel
from src.models.request import RequestLikes
from src.models.user import User

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=["HS384"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        likes = db.query(RequestLikes).filter(RequestLikes.user_id == user.id).all()
        request_ids = [like.request_id for like in likes]

        user_details = UserModel(id=user.id, email=user.email, username=user.username, phone_number=user.phone_number,
                                 role=user.role, favourites=request_ids)
        print(user.id)
        return user_details
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def send_password_email(email_user, password_user):
    smtp_server = settings.SMTP_SERVER
    port = settings.SMTP_PORT
    email_address = settings.HOST_EMAIL
    password = settings.EMAIL_PASS
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.login(email_address, password)

        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = email_user
        msg['Subject'] = f'[Front Support] Скидання паролю для {email_user}'
        msg_id = make_msgid(domain=settings.DOMAIN_NAME)
        msg['Message-ID'] = msg_id

        html = f'''
            <table style="Margin:0;background:#fff;border-collapse:collapse;border-spacing:0;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;height:100%;line-height:1.7;margin:0;padding:0;text-align:left;vertical-align:top;width:100%;display: flex;justify-content: flex-start;">
     <tbody style="
"><tr style="padding:0;text-align:left;vertical-align:top">
       <td style="Margin:0;border-collapse:collapse!important;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;text-align:left;vertical-align:top;word-wrap:break-word">

        <table align="center" style="Margin:0 auto;background:#fff;border-collapse:collapse;border-spacing:0;float:none;margin:0 auto;padding:0;text-align:center;vertical-align:top;width:580px"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><td style="Margin:0;border-collapse:collapse!important;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;text-align:left;vertical-align:top;word-wrap:break-word">
          <table style="border-collapse:collapse;border-spacing:0;display:center;padding:0;text-align:left;vertical-align:top;width:100%"><tbody><tr style="padding:0;text-align:center;vertical-align:top">

           <th style="Margin:0 auto;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0 auto;padding:0;padding-left:6px;padding-top:16px;padding-right:8px;text-align:center;width:274px"></th>

             </tr></tbody></table>
             <table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><td height="20px" style="Margin:0;border-collapse:collapse!important;color:#344a5e;font-family:Tahoma,sans-serif;font-size:20px;font-weight:400;line-height:20px;margin:0;padding:0;text-align:left;vertical-align:top;word-wrap:break-word">&nbsp;
             <table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top">
               <tbody>
                 <tr style="padding:0;text-align:left;vertical-align:top">
                   <td style="Margin:0;border-collapse:collapse!important;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;padding-left:0;text-align:left;vertical-align:top;word-wrap:break-word"><span class="im">

                    <h1 style="Margin:0;Margin-bottom:0;color:inherit;font-family:Tahoma,sans-serif;font-size:25px;font-weight:700;line-height:1.5;margin:0;margin-bottom:0;padding:0;text-align:left;padding-left:22px;padding-right:16px;padding-left:22px;padding-right:16px;color: #344a5e;word-wrap:normal">Пароль успішно змінено</h1>
                       <table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><td height="20px" style="Margin:0;border-collapse:collapse!important;color:#344a5e;font-family:Tahoma,sans-serif;font-size:20px;font-weight:400;line-height:20px;margin:0;padding:0;padding-left:16px;text-align:left;vertical-align:top;word-wrap:break-word">&nbsp;</td></tr></tbody></table>

                       <p style="Margin:0;Margin-bottom:10px;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;margin-bottom:10px;padding:0;text-align:left;padding-left:22px;padding-right:16px">
                            Для авторизації в аккаунт використовуйте:</p>
                          </span><ul>
                              <li><b>Пошта:</b> <a href="mailto:{email_user}" target="_blank">{email_user}</a></li>
                              <li><b>Новий пароль:</b> {password_user}</li><span class="im">
                              <small style="
                                    color: #344a5e;
                                ">за потреби змініть його у профілі</small>
                              </span></ul>
                       <table style="border-collapse:collapse;border-spacing:0;display:table;padding:0;text-align:left;vertical-align:top;width:100%"><tbody><tr style="padding:0;text-align:left;vertical-align:top">
                          <th style="Margin:0 auto;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0 auto;padding:0;padding-bottom:16px;padding-left:22px;padding-right:8px;text-align:left;width:129px"><table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top;width:100%"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><th style="Margin:0;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;text-align:left">
                            <table style="Margin:0 0 16px 0;border-collapse:collapse;border-spacing:0;margin:0 0 16px;padding:0;text-align:left;vertical-align:top;width:auto!important"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><td style="Margin:0;border-collapse:collapse!important;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;text-align:left;vertical-align:top;word-wrap:break-word"><table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top;width:100%"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><td style="Margin:0;background:0 0;border:1px solid transparent;border-collapse:collapse!important;color:#fff;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;text-align:left;vertical-align:top;word-wrap:break-word">


                              <a href="https//:{settings.DOMAIN_NAME}/auth" style="Margin:0;background-color:#5b40ff!important;border-radius:.5rem;color:#fff!important;display:inline-block;font-family:Tahoma,sans-serif;font-size:16px;font-weight:400;line-height:1.5;margin:0;padding:7px 37px!important;text-align:left;text-decoration:none;text-transform:normal;white-space:nowrap!important" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://{settings.DOMAIN_NAME}/auth&amp;source=gmail&amp;ust=1714396499627000&amp;usg=AOvVaw37TWKSV1IxJ38NLvd8eTQG" jslog="32272; 1:WyIjdGhyZWFkLWY6MTc5NzU3ODU5NjEwMjcwMjc4MiJd; 4:WyIjbXNnLWY6MTc5NzU4NDM4MTIyMzE5NDEwOCJd">Перейти до авторизації</a>

                            </td></tr></tbody></table></td></tr></tbody></table></th></tr></tbody></table></th><th style="Margin:0 auto;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0 auto;padding:0;padding-bottom:16px;padding-left:22px;padding-right:10px;text-align:left;width:370px"><table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top;width:100%"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><th style="Margin:0;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;text-align:left">
                            </th></tr></tbody></table></th></tr></tbody></table>
             <table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><td height="20px" style="Margin:0;border-collapse:collapse!important;color:#344a5e;font-family:Tahoma,sans-serif;font-size:20px;font-weight:400;line-height:20px;margin:0;padding:0;text-align:left;vertical-align:top;word-wrap:break-word">&nbsp;</td></tr></tbody></table>
             <table style="border-collapse:collapse;border-spacing:0;display:table;padding:0;text-align:left;vertical-align:top;width:100%"><tbody><tr style="padding:0;text-align:left;vertical-align:top">
               <th style="Margin:0 auto;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0 auto;padding:0;padding-bottom:16px;padding-left:16px;padding-right:22px;text-align:left;width:564px"><table style="border-collapse:collapse;border-spacing:0;padding:0;text-align:left;vertical-align:top;width:100%"><tbody><tr style="padding:0;text-align:left;vertical-align:top"><th style="Margin:0;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0;text-align:left"></th>
                <th style="Margin:0;color:#344a5e;font-family:Tahoma,sans-serif;font-size:14px;font-weight:400;line-height:1.7;margin:0;padding:0!important;text-align:left;width:0"></th></tr></tbody></table></th>
             </tr></tbody></table>
           </td></tr></tbody></table>
       </td>
     </tr>
   </tbody></table>
</td></tr></tbody></table></td></tr></tbody></table>
        '''
        msg.attach(MIMEText(html, 'html'))

        server.send_message(msg)
        server.quit()
    except smtplib.SMTPException as e:
        raise e






