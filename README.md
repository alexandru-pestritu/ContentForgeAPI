# ContentForge API

ContentForge is an API built with **FastAPI** for automating the creation of blog articles on a WordPress site. This application is designed to support **affiliate marketing** by generating high-quality content efficiently. The UI for ContentForge is built with Angular and is available [here](https://github.com/alexandru-pestritu/ContentForgeUI).

## ✨ Features

- **Affiliate Store Management** 🏪  
  Users can add and manage affiliate stores in the database effortlessly. Each store is defined with relevant details, including the store name, base URL, and optional favicon, enabling seamless integration and organization of products linked to specific stores.

- **Automated Product Data Scraping** 🛒  
  Users can add products by providing the product's affiliate URL. The API utilizes **BeautifulSoup4** and **Crawlbase** to scrape detailed product information, including descriptions, specifications, images, and other relevant data. This automation ensures that the most current and accurate information is available for use in articles, eliminating manual entry.

- **Article Creation with Product Integration** ✍️  
  Users can create articles while specifying the associated products. The articles can incorporate scraped product data, enhancing the content's value and relevance to readers. This feature allows users to build comprehensive articles that naturally incorporate product recommendations.

- **AI Content Generation for Products and Articles** 🤖  
  ContentForge integrates with **EdenAI**, a unified API for accessing multiple AI models, allowing users to generate high-quality AI content. Users can create product reviews, highlight pros and cons, and generate various sections of articles, including introductions, buyer's guides, FAQs, and conclusions. This flexibility enables tailored content that resonates with target audiences.

- **Custom Prompt Creation** 🔍  
  Users can create and manage custom prompts with placeholders for products and articles. These placeholders dynamically insert values from product or article models, allowing for highly customizable content generation. This feature empowers users to refine the tone and style of the AI-generated content to align with their brand voice.

- **Gutenberg Blocks Layout for WordPress** 📝  
  Once an article is finalized, users can publish it directly to their WordPress site. The API generates a Gutenberg blocks layout based on the article's content and associated products, ensuring the article is well-structured and visually appealing when published. This integration simplifies the publishing process, allowing users to focus on content creation rather than technical details.

- **Stock Monitoring and Check Logs** 📉  
  The API tracks product availability and logs stock checks, providing users with insights into stock levels and historical data. Users can view detailed logs that include check times, in-stock counts, and out-of-stock counts, enabling better inventory management and timely updates to articles based on product availability.

- **SEO Optimization Features** 🚀  
  Articles can be enhanced with SEO features such as keywords, meta titles, and meta descriptions. Users can input these details while creating articles, improving the chances of their content ranking higher in search engine results and attracting more organic traffic.

- **Secure Authentication & User Management** 🔒  
  ContentForge ensures secure access to its API through JWT token-based authentication. Users must authenticate to access specific operations, safeguarding sensitive data and allowing for effective user management within the application.


## 🚀 Installation

To set up the project, follow these steps:

1. Clone the repository:
   
   ```bash
   git clone https://github.com/alexandru-pestritu/ContentForgeAPI.git
   cd contentforgeapi
   ```
3. Create a virtual environment and activate it:
   
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
5. Install the required dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```
7. Set up your environment variables by copying the ```.env-template.txt``` to .env and modifying it as needed.
   
9. Run the database migrations:
    
   ```bash
   alembic upgrade head
   ```

## 🏃 Running the Application
You can start the application using the following command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access the API at ```http://localhost:8000```.


## 📡 API Endpoints

### Stores
- **Create Store**  
  `POST /api/v1/stores/`  
  Create a new store in the database.

- **Read Stores**  
  `GET /api/v1/stores/`  
  Retrieve a list of all stores.

- **Read Store**  
  `GET /api/v1/stores/{store_id}`  
  Retrieve details of a specific store by ID.

- **Update Store**  
  `PUT /api/v1/stores/{store_id}`  
  Update an existing store's details.

- **Delete Store**  
  `DELETE /api/v1/stores/{store_id}`  
  Remove a store from the database.

### Products
- **Create Product**  
  `POST /api/v1/products/`  
  Add a new product, retrieving details through data scraping.

- **Read Products**  
  `GET /api/v1/products/`  
  Get a list of all products.

- **Read Out of Stock Products**  
  `GET /api/v1/products/out-of-stock`  
  Retrieve a list of products that are out of stock.

- **Read Product**  
  `GET /api/v1/products/{product_id}`  
  Get details of a specific product by ID.

- **Update Product**  
  `PUT /api/v1/products/{product_id}`  
  Update details of an existing product.

- **Delete Product**  
  `DELETE /api/v1/products/{product_id}`  
  Remove a product from the database.

### Articles
- **Create Article**  
  `POST /api/v1/articles/`  
  Add a new article, linking associated products.

- **Read Articles**  
  `GET /api/v1/articles/`  
  Retrieve a list of all articles.

- **Read Latest Articles**  
  `GET /api/v1/articles/latest`  
  Get the most recent articles.

- **Read Article**  
  `GET /api/v1/articles/{article_id}`  
  Retrieve details of a specific article by ID.

- **Update Article**  
  `PUT /api/v1/articles/{article_id}`  
  Update an existing article.

- **Delete Article**  
  `DELETE /api/v1/articles/{article_id}`  
  Remove an article from the database.

### Prompts
- **Create Prompt**  
  `POST /api/v1/prompts/`  
  Add a new AI prompt for content generation.

- **Read Prompts**  
  `GET /api/v1/prompts/`  
  Retrieve a list of all prompts.

- **Read Prompts by Type**  
  `GET /api/v1/prompts/{prompt_type}`  
  Get prompts filtered by type and optional subtype.

- **Read Prompt**  
  `GET /api/v1/prompts/{prompt_id}`  
  Retrieve details of a specific prompt by ID.

- **Update Prompt**  
  `PUT /api/v1/prompts/{prompt_id}`  
  Update an existing prompt.

- **Delete Prompt**  
  `DELETE /api/v1/prompts/{prompt_id}`  
  Remove a prompt from the database.

- **Get Types and Subtypes**  
  `GET /api/v1/prompts/types-subtypes/`  
  Retrieve available prompt types and subtypes.

- **Get Placeholders**  
  `GET /api/v1/prompts/placeholders/{type}`  
  Get placeholders for a specific prompt type.

### WordPress Integration
- **Get WordPress Users**  
  `GET /api/v1/wordpress/users`  
  Retrieve a list of users from WordPress.

- **Get WordPress Categories**  
  `GET /api/v1/wordpress/categories`  
  Retrieve a list of categories from WordPress.

### AI Content Generation
- **Get AI Providers**  
  `GET /api/v1/ai/providers`  
  List available AI content generation providers.

- **Generate Product AI Text**  
  `POST /api/v1/ai/generate-product-text`  
  Generate AI text for product reviews and details.

- **Generate Article AI Text**  
  `POST /api/v1/ai/generate-article-text`  
  Generate AI content for articles (introduction, FAQs, etc.).

### Widgets
- **Generate Product Content**  
  `POST /api/v1/widgets/generate/product`  
  Generate content for products based on predefined templates.

- **Generate Article Content**  
  `POST /api/v1/widgets/generate/article`  
  Generate content for articles using custom templates.

### Dashboard
- **Read Dashboard Stats**  
  `GET /api/v1/dashboard/stats`  
  Retrieve statistics related to articles, products, and overall performance.

### Stock Check Logs
- **Read Stock Check Logs**  
  `GET /api/v1/stock-check-logs/`  
  Retrieve logs of stock checks and product availability over time.

### Authentication
- **Login for Access Token**  
  `POST /api/v1/login`  
  Authenticate users and obtain an access token.

- **Refresh Access Token**  
  `POST /api/v1/token/refresh`  
  Refresh the user's access token for continued access.

## 🌐 Deployment

### Docker

This project includes a Dockerfile, allowing you to easily build and run the application in a containerized environment. The Dockerfile sets up the application with all necessary dependencies and environment variables.

#### Building the Docker Image

To deploy the application using Docker, follow these steps:

1. **Build the Docker Image**  
   Navigate to the root directory of the project and run the following command to build the Docker image:

   ```bash
   docker build -t contentforgeapi .
   ```

2. **Run the Docker Container**
   After building the image, you can run a container using the following command:

   ```bash
   docker run -d -p 8000:8000 --env-file .env contentforgeapi
   ```
  Make sure to create a ```.env``` file in the root directory of your project with environment variables from ```.env-template.txt``` file before running the Docker container.
  Replace 8000 with the desired port if necessary. This command will start the FastAPI application, exposing it on the specified port.
