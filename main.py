import flet as ft
import requests as rq
import io, base64
import qrcode
import threading
import time

def main(page: ft.Page):
    black = "#000000"
    blue = '#3D5AF1'
    light_blue = '#40A2D8'
    of_white = '#F0EDCF'

    page.bgcolor = black
    page.title = "URL Shortener"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.update()

    def reset_button_text(button, original_text, delay=3):
        """Reset button text after delay"""
        def reset():
            time.sleep(delay)
            try:
                button.text = original_text
                page.update()
            except:
                pass
        
        thread = threading.Thread(target=reset)
        thread.daemon = True
        thread.start()

    # Create all UI elements first
    title = ft.Text("URL Shortener", size=24, color=of_white, weight=ft.FontWeight.BOLD)
    
    long_url_input = ft.TextField(
        label="Enter Long URL (e.g., https://example.com)", 
        border_color=blue, 
        border_width=2, 
        border_radius=10, 
        color=of_white, 
        height=60,
        text_size=16,
        keyboard_type=ft.KeyboardType.URL
    )

    # Results container (initially empty)
    results_container = ft.Container(
        content=ft.Column([], spacing=15),
        visible=False,
        padding=ft.padding.all(15),
        margin=ft.margin.only(top=20),
        border=ft.border.all(1, blue),
        border_radius=15,
        bgcolor=black
    )

    def shorten(e):
        long_url = long_url_input.value.strip()
        if not long_url:
            dlg = ft.AlertDialog(
                modal=True, 
                title=ft.Text("Empty input"), 
                content=ft.Text("Please enter a long URL"), 
                actions=[ft.TextButton("OK", on_click=lambda ev: page.close(dlg))]
            )
            page.open(dlg)
            return

        # Hide results and show loading
        results_container.visible = False
        shorten_button.text = "Loading..."
        shorten_button.disabled = True
        page.update()

        try:
            api_url = "https://tinyurl.com/api-create.php"
            response = rq.get(api_url, params={"url": long_url}, timeout=10)
            short_url = response.text.strip()
        except Exception:
            short_url = "Error"

        shorten_button.text = "Shorten URL"
        shorten_button.disabled = False

        if short_url == "Error" or not short_url.startswith("http"):
            dlg = ft.AlertDialog(
                modal=True, 
                title=ft.Text("Error"), 
                content=ft.Text("Please enter a valid URL (e.g., https://example.com)"), 
                actions=[ft.TextButton("OK", on_click=lambda ev: page.close(dlg))]
            )
            page.open(dlg)
            page.update()
            return

        # Create results
        display_results(short_url)

    def display_results(short_url):
        # Short URL display
        short_url_display = ft.TextField(
            label="Short URL", 
            border_color=blue, 
            border_width=2, 
            border_radius=10, 
            color=of_white, 
            read_only=True, 
            value=short_url,
            multiline=True,
            min_lines=1,
            max_lines=3,
            text_size=14
        )

        # QR Code
        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=8, border=2)
            qr.add_data(short_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color=blue, back_color=of_white)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode("utf-8")
            qr_img = ft.Image(src_base64=img_b64, width=180, height=180, fit=ft.ImageFit.CONTAIN)
        except Exception:
            qr_img = ft.Text("QR Code generation failed", color=of_white)

        # Button actions
        def copy_action(ev):
            try:
                page.set_clipboard(short_url)
                copy_button.text = "Copied ✅"
                page.update()
                reset_button_text(copy_button, "Copy")
            except Exception:
                copy_button.text = "Copy Failed"
                page.update()
                reset_button_text(copy_button, "Copy")

        def open_action(ev):
            try:
                page.launch_url(short_url)
                open_button.text = "Opened ✅"
                page.update()
                reset_button_text(open_button, "Open")
            except Exception:
                open_button.text = "Open Failed"
                page.update()
                reset_button_text(open_button, "Open")

        def clear_action(ev):
            try:
                long_url_input.value = ""
                results_container.visible = False
                clear_button.text = "Cleared ✅"
                page.update()
                reset_button_text(clear_button, "Clear")
            except Exception:
                clear_button.text = "Clear Failed"
                page.update()
                reset_button_text(clear_button, "Clear")

        # Buttons
        copy_button = ft.ElevatedButton("Copy", bgcolor=light_blue, color=of_white, on_click=copy_action, expand=True, height=50)
        open_button = ft.ElevatedButton("Open", bgcolor=light_blue, color=of_white, on_click=open_action, expand=True, height=50)
        clear_button = ft.ElevatedButton("Clear", bgcolor=light_blue, color=of_white, on_click=clear_action, expand=True, height=50)

        buttons_row = ft.Row([copy_button, open_button, clear_button], alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=10)

        # Update results container content
        results_container.content = ft.Column([
            short_url_display,
            ft.Container(content=qr_img, alignment=ft.alignment.center),
            buttons_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        
        results_container.visible = True
        page.update()

    shorten_button = ft.ElevatedButton(
        "Shorten URL", 
        bgcolor=blue, 
        color=of_white, 
        height=60, 
        on_click=shorten,
        width=200
    )

    # Add all elements to page
    page.add(
        ft.Column([
            title,
            long_url_input,
            ft.Container(content=shorten_button, alignment=ft.alignment.center),
            results_container
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20)
    )
    page.update()

ft.app(target=main)