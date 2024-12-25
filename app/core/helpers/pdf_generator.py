from weasyprint import HTML
from jinja2 import Template
from app.db import User
from app.core.helpers.logging import logger
from sqlalchemy.orm import Session
from typing import List, Dict
import io

def generate_users_pdf(users: list[Dict]):
    logger.info(f"####DATA: {users}")

    html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 5px; border: 1px solid #ddd; }
                th { background-color: #f4f4f4; }
            </style>
        </head>
        <body>
            <h2>List of Users</h2>
            <table>
                <thead>
                    <tr>
                        <th style="text-align: center">Email</th>
                        <th>Active</th>
                        <th>Superuser</th>
                        <th>Verified</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user.email }}</td>
                        <td>{{ user.is_active }}</td>
                        <td>{{ user.is_superuser }}</td>
                        <td>{{ user.is_verified }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """

    # Render the HTML with Jinja2
    template = Template(html_template)
    html_content = template.render(users=users)

    # Generate PDF from HTML
    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)

    return pdf_file