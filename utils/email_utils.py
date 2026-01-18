import random
from flask_mail import Message
from flask import current_app, render_template_string

# Fungsi untuk generate kode OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Fungsi untuk mengirim email OTP dengan desain modern
def send_email_otp(email, otp):
    subject = "Verifikasi Akun Anda - Kode OTP Sibatikgal"

    # Template HTML Email
    html = render_template_string("""
    <html>
    <body style="font-family: 'Arial', sans-serif; color: #3a2718; background: #fdf7f0; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 20px auto; padding: 20px; background-color: #ffffff; border-radius: 12px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);">
            <header style="text-align: center; padding: 15px 20px; background: #bc9665; border-radius: 10px 10px 0 0; color: #ffffff;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 1px;">Konfirmasi Email Anda</h1>
            </header>
            <section style="padding: 30px; text-align: center; color: #6b4e3d;">
                <p style="margin: 0; font-size: 16px; font-weight: 500;">Halo,</p>
                <p style="font-size: 16px; margin-top: 10px;">Terima kasih telah bergabung dengan <strong>BatikKara</strong>. Untuk melanjutkan penggunaan akun Anda, silakan konfirmasi alamat email Anda menggunakan kode di bawah ini:</p>
                <div style="margin: 20px auto; padding: 15px 20px; font-size: 36px; font-weight: bold; color: #af7441; background-color: #fae8d6; border: 2px solid #bc9665; border-radius: 8px; display: inline-block;">
                    {{ otp }}
                </div>
                <p style="margin-top: 20px; font-size: 14px; color: #6b4e3d;">Kode ini akan kadaluarsa dalam <strong>5 menit</strong>. Jangan bagikan kode ini kepada siapa pun untuk menjaga keamanan akun Anda.</p>
            </section>
            <footer style="background: #f7f0eb; text-align: center; padding: 15px; border-top: 1px solid #dbcbb1; border-radius: 0 0 10px 10px;">
                <p style="font-size: 14px; color: #946644;">
                    Jika Anda tidak meminta kode ini, abaikan saja email ini. Untuk bantuan, hubungi tim dukungan kami.
                </p>
                <p style="font-size: 12px; color: #8b5e3c;">&copy; 2026 BatikKara. All Rights Reserved.</p>
            </footer>
        </div>
    </body>
    </html>
    """, otp=otp)

    # Buat objek email
    msg = Message(subject=subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[email])
    
    # Tambahkan template HTML ke email
    msg.html = html
    
    # Kirim email menggunakan instance Flask-Mail
    current_app.mail.send(msg)