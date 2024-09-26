import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage


class EmailSender:

    def __init__(
        self,
        smtp_server: str,
        username: str,
        password: str,
        port: int = 587,
        use_tls: bool = True,
    ) -> None:
        self.smtp_server: str = smtp_server
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.use_tls: bool = use_tls

    def send_email(
        self,
        subject,
        body,
        to: str,
        from_: str | None = None,
        cc: str | None = None,
        bcc: list = [],
        html=False,
        attachments=None,
        images=None,
    ) -> None:

        msg: MIMEMultipart = MIMEMultipart()
        msg["From"] = from_ if from_ else self.username
        msg["To"] = to
        msg["Subject"] = subject

        if cc:
            msg["Cc"] = cc

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file_path in attachments:
                self._add_attachment(msg, file_path)

        if images:
            for cid, img_path in images.items():
                self._add_inline_image(msg, img_path, cid)

        self._send_via_smtp(msg, from_, to, cc, bcc)

    def _add_attachment(self, msg, file_path) -> None:
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=file_path)
        part["Content-Disposition"] = f'attachment; filename="{file_path}"'
        msg.attach(part)

    def _add_inline_image(self, msg, img_path, cid) -> None:
        with open(img_path, "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header("Content-ID", f"<{cid}>")
            msg.attach(img)

    def _send_via_smtp(
        self,
        msg,
        from_,
        to: str,
        cc: str | None = None,
        bcc: list | None = None,
    ) -> None:
        if from_ is None:
            from_ = self.username

        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)

                recipients: list[str] = [to]
                if cc:
                    recipients += cc.split(",")  # Dividir si es una cadena
                if bcc:
                    recipients += bcc

                server.sendmail(from_, recipients, msg.as_string())
        except smtplib.SMTPException as e:
            raise RuntimeError(f"Error sending email: {e}")

