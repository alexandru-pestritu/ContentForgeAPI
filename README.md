# ContentForge API

ContentForge is an API built with **FastAPI** for automating the creation and management of blog articles on WordPress sites. This application is designed to support **affiliate marketing** by streamlining the process of managing affiliate stores, products, and AI-generated content. The UI for ContentForge is built with Angular and is available [here](https://github.com/alexandru-pestritu/ContentForgeUI).

## ✨ Features

### **Multi-Blog Support** 📝
Manage multiple blogs independently, with separate configurations for stores, products, articles, and prompts for each blog. This allows users to publish relevant content directly to the corresponding WordPress blogs.

### **Affiliate Store Management** 🏪
Users can add and manage affiliate stores within the app. Stores are defined with relevant details such as store name, base URL, and optional favicon, making it easier to organize products by their source.

### **Automated Product Data Scraping** 🛒
Add products by providing the product's affiliate URL. The API uses **BeautifulSoup4** and **Crawlbase** to scrape essential product information, such as descriptions, specifications, and images, ensuring accuracy and efficiency.

### **Article Creation with Product Integration** ✍️
Create articles with dynamically integrated product data to build comprehensive, engaging blog content that includes recommendations, reviews, and product details.

### **AI Content Generation** 🤖
Integrate with **EdenAI** to generate:
- Product reviews, pros, and cons.
- Article sections, including introductions, buyer's guides, FAQs, and conclusions.
- Custom prompts for tailored AI-generated content.

### **Import and Export CSV** 📂
Import and export stores, products, articles, and prompts via CSV files. Import tasks run with websocket-based feedback, updating the frontend with the status of each item.

### **Database Normalization and PostgreSQL Migration** 🗄️
The database has been normalized and migrated to PostgreSQL for enhanced performance, scalability, and better data organization.

### **Settings Management** ⚙️
A comprehensive settings page to manage:
- API keys for scraping and AI content generation.
- Image resolution, file names, and alt text templates.
- AI provider and model selection.
- Maximum token length, temperature, and other content generation parameters.

### **Setup Wizard** 🚀
A guided setup process for first-time users to:
- Create an admin account.
- Configure API keys for web scraping and AI services.
- Add the first blog for immediate use.

### **Gutenberg Block Layout for WordPress** 📝
Publish articles directly to WordPress in a visually appealing Gutenberg block format.

### **Stock Monitoring and Logging** 📉
Track product availability and view detailed stock check logs, including timestamps and product statuses.

### **SEO Optimization** 🚀
Input SEO metadata such as keywords, meta titles, and meta descriptions while creating articles to improve organic search performance.

### **Secure Authentication & User Management** 🔒
Access to the API is secured through JWT token-based authentication, ensuring that only authorized users can manage blogs and content.

## 🚀 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL

### Steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alexandru-pestritu/ContentForgeAPI.git
   cd ContentForgeAPI
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Copy `.env-template.txt` to `.env` and update it with the necessary configuration.

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

## 🏃 Running the Application

Start the API server with:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Access the API at `http://localhost:8000`.

## 📊 API Endpoints

### **Setup**
- **Check Setup Status:** `GET /api/v1/setup/status`
- **Step 1 (User Creation):** `POST /api/v1/setup/step1`
- **Step 2 (API Keys Configuration):** `POST /api/v1/setup/step2`
- **Step 3 (First Blog Configuration):** `POST /api/v1/setup/step3`
- **Finalize Setup:** `POST /api/v1/setup/complete`

### **Blogs**
- **Create Blog:** `POST /api/v1/blogs/`
- **Read Blogs:** `GET /api/v1/blogs/`
- **Read Blog by ID:** `GET /api/v1/blogs/{blog_id}`
- **Update Blog:** `PUT /api/v1/blogs/{blog_id}`
- **Delete Blog:** `DELETE /api/v1/blogs/{blog_id}`

### **Stores**
- **Create Store:** `POST /api/v1/{blog_id}/stores/`
- **Read Stores:** `GET /api/v1/{blog_id}/stores/`
- **Read Store by ID:** `GET /api/v1/{blog_id}/stores/{store_id}`
- **Update Store:** `PUT /api/v1/{blog_id}/stores/{store_id}`
- **Delete Store:** `DELETE /api/v1/{blog_id}/stores/{store_id}`

### **Products**
- **Create Product:** `POST /api/v1/{blog_id}/products/`
- **Read Products:** `GET /api/v1/{blog_id}/products/`
- **Read Out-of-Stock Products:** `GET /api/v1/{blog_id}/products/out-of-stock`
- **Read Product by ID:** `GET /api/v1/{blog_id}/products/{product_id}`
- **Update Product:** `PUT /api/v1/{blog_id}/products/{product_id}`
- **Delete Product:** `DELETE /api/v1/{blog_id}/products/{product_id}`

### **Articles**
- **Create Article:** `POST /api/v1/{blog_id}/articles/`
- **Read Articles:** `GET /api/v1/{blog_id}/articles/`
- **Read Latest Articles:** `GET /api/v1/{blog_id}/articles/latest`
- **Read Article by ID:** `GET /api/v1/{blog_id}/articles/{article_id}`
- **Update Article:** `PUT /api/v1/{blog_id}/articles/{article_id}`
- **Delete Article:** `DELETE /api/v1/{blog_id}/articles/{article_id}`

### **Prompts**
- **Create Prompt:** `POST /api/v1/{blog_id}/prompts/`
- **Read Prompts:** `GET /api/v1/{blog_id}/prompts/`
- **Read Prompt by Type:** `GET /api/v1/{blog_id}/prompts/{prompt_type}`
- **Read Prompt by ID:** `GET /api/v1/{blog_id}/prompts/{prompt_id}`
- **Update Prompt:** `PUT /api/v1/{blog_id}/prompts/{prompt_id}`
- **Delete Prompt:** `DELETE /api/v1/{blog_id}/prompts/{prompt_id}`
- **Get Available Prompt Types and Subtypes:** `GET /api/v1/{blog_id}/prompts/types-subtypes/`

### **WordPress Integration**
- **Get WordPress Users:** `GET /api/v1/{blog_id}/wordpress/users`
- **Get WordPress Categories:** `GET /api/v1/{blog_id}/wordpress/categories`

### **AI Content Generation**
- **Get AI Providers:** `GET /api/v1/{blog_id}/ai/providers`
- **Generate Product AI Text:** `POST /api/v1/{blog_id}/ai/generate-product-text`
- **Generate Article AI Text:** `POST /api/v1/{blog_id}/ai/generate-article-text`

### **Import/Export**
- **Import CSV:** `POST /api/v1/{blog_id}/import/`
- **Retry Failed Imports:** `POST /api/v1/{blog_id}/import/{task_id}/retry`
- **Export CSV:** `GET /api/v1/{blog_id}/export/`

### **Settings**
- **Read Settings:** `GET /api/v1/settings/`
- **Create Setting:** `POST /api/v1/settings/`
- **Read Setting by Key:** `GET /api/v1/settings/{key}`
- **Update Setting:** `PUT /api/v1/settings/{key}`
- **Delete Setting:** `DELETE /api/v1/settings/{key}`

### **Stock Check Logs**
- **Read Stock Check Logs:** `GET /api/v1/{blog_id}/stock-check-logs/`

### **Authentication**
- **Login:** `POST /api/v1/login`
- **Refresh Access Token:** `POST /api/v1/token/refresh`

## 🌐 Deployment

### **Docker**
This project includes a Dockerfile for containerized deployment.

1. **Build Docker Image:**
   ```bash
   docker build -t contentforgeapi .
   ```

2. **Run Docker Container:**
   ```bash
   docker run -d -p 8000:8000 --env-file .env contentforgeapi
   ```

Ensure the `.env` file contains your environment variables.

## 🖼️ Database Diagram
![ContentForge_database_diagram](https://github.com/user-attachments/assets/e0646d11-9a72-4282-81d0-2d04e330b6b9)


## 🛠️ Contributing
Contributions are welcome! Fork the repository, make your changes, and submit a pull request.

## 📄 License
ContentForge is licensed under the MIT License.
