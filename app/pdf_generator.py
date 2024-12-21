from weasyprint import HTML
from jinja2 import Template
from app.models.employer import Employer
from sqlalchemy.orm import Session
import io

def generate_employers_pdf(employers: list[Employer]):

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
          <h2>List of Employers</h2>
          <table>
              <thead>
                  <tr>
                      <th style="text-align: center">ID</th>
                      <th>First Name</th>
                      <th>Last Name</th>
                      <th>Email</th>
                  </tr>
              </thead>
              <tbody>
                  {% for employer in employers %}
                  <tr>
                      <td style="text-align: center">{{ employer.id }}</td>
                      <td>{{ employer.first_name }}</td>
                      <td>{{ employer.last_name }}</td>
                      <td>{{ employer.email }}</td>
                  </tr>
                  {% endfor %}
              </tbody>
          </table>
      </body>
      </html>
      """

    # Render the HTML with Jinja2
    template = Template(html_template)
    html_content = template.render(employers=employers)

    # Generate the PDF amd save it to a buffer
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer