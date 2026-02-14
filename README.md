# Imtiaz E-commerce Project

A comprehensive, feature-rich e-commerce platform built with Django, featuring custom user management, product/category handling, and secure payments via Stripe.

## 🚀 Features

- **Custom Authentication**: Specialized user and superuser models using `AbstractBaseUser`.
- **Product Management**:
  - Category-based organization.
  - Automated slug generation for SEO-friendly URLs.
  - Discount calculation logic.
  - Multi-image support for products.
- **Shopping Cart**:
  - Item quantity management.
  - Real-time total calculation.
- **Secure Payments**:
  - Full [Stripe](https://stripe.com/) integration.
  - Secure checkout flow.
  - Webhook support for payment status updates (`payment_intent.succeeded`, `payment_intent.payment_failed`).
- **Order Management**:
  - Detailed shipping address tracking.
  - Order status tracking (Pending, Completed, Cancelled).
  - Transaction history for users.
- **Responsive Frontend**: Clean and modern UI for indexing, shopping, and product details.

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Django 5.1.4
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (default)
- **Payments**: Stripe API
- **Utilities**: Pillow (Image handling), Requests, Tzdata

## ⚙️ Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd Imtiaz
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Environmental Variables**:
   You should set your Stripe keys as environment variables for security. You can set them in your terminal or use a `.env` file (ensure `python-dotenv` is installed):
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_API_KEY`
   - `STRIPE_WEBHOOK_SECRET`

   Example (Windows PowerShell):

   ```powershell
   $env:STRIPE_API_KEY="sk_test_..."
   ```

6. **Run the server**:

   ```bash
   python manage.py runserver
   ```

## 📂 Project Structure

- `ecom/`: Project configuration and settings.
- `imtiaz/`: Core application containing models, views, and business logic.
- `static/` & `staticfiles/`: CSS, JS, and image assets.
- `templates/`: HTML templates for the frontend.
- `media/`: User-uploaded product and category images.

## 💳 Stripe Integration Note

This project uses Stripe Payment Intents. Ensure your webhook endpoint is correctly configured to point to `/imtiaz/stripe-webhook/` (check `urls.py` for exact path) to handle payment success/failure notifications asynchronously.

---
Built with ❤️ using Django.
