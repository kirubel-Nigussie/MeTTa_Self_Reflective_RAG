# MeTTa Self-Reflective RAG System

A sophisticated AI-powered chatbot system that provides intelligent, self-correcting answers about the MeTTa Standard Library documentation. The system features JWT authentication, real-time chat interface, and advanced self-reflection capabilities.

## 🌟 Features

### 🔐 **Authentication System**
- **JWT-based authentication** with secure token management
- **User registration and login** with password strength validation
- **Protected routes** for all sensitive operations
- **Session persistence** across browser refreshes
- **User profile management** with avatar display

### 🧠 **Self-Reflective RAG Pipeline**
- **Multi-stage reasoning process** with automatic self-correction
- **Document relevance checking** (ISREL)
- **Query rewriting** for better retrieval
- **Answer generation** with context awareness
- **Factuality verification** (ISSUP) - checks if answers are supported by documents
- **Usefulness assessment** (ISUSE) - evaluates answer quality
- **Automatic refinement** when critiques fail
- **Chain of thought visualization** showing the AI's reasoning process

### 💬 **Modern Chat Interface**
- **Real-time chat** with typing indicators
- **Responsive design** that works on desktop and mobile
- **Dark theme** with gradient accents
- **Trace visualization** showing each step of the reasoning process
- **User sidebar** with profile information and logout
- **PDF upload capability** for adding new documents

### 🔧 **Technical Features**
- **Google Gemini 2.0 Flash** for advanced language processing
- **ChromaDB** for efficient vector storage and semantic search
- **Sentence Transformers** for high-quality embeddings
- **LangChain** for text processing and chunking
- **SQLAlchemy** for robust database management
- **Flask** backend with CORS support
- **Next.js** frontend with React 19

## 🏗️ Architecture

```
MeTTa_Self_Reflective_RAG/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── services/           # Business logic services
│   │   ├── auth.py         # Authentication service
│   │   ├── critique.py     # Self-reflection logic
│   │   ├── llm_client.py   # Gemini API client
│   │   └── vector_store.py # ChromaDB operations
│   ├── core/               # Core pipeline logic
│   └── data/               # Database and uploads
├── frontend/               # Next.js React application
│   ├── src/app/           # React components
│   │   ├── contexts/      # Authentication context
│   │   ├── login/         # Login page
│   │   ├── signup/        # Registration page
│   │   └── page.js        # Main chat interface
│   └── public/            # Static assets
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** for the backend
- **Node.js 18+** for the frontend
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd MeTTa_Self_Reflective_RAG
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
echo "JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production" >> .env
echo "DATABASE_URL=sqlite:///./data/users.db" >> .env

# Start the backend server
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:3000`

### 4. Access the Application

1. **Open your browser** and go to `http://localhost:3000`
2. **Create an account** or **login** with existing credentials
3. **Upload a PDF** document about MeTTa (optional)
4. **Start chatting** with the AI about MeTTa documentation

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/profile` - Get user profile (protected)

### Core Functionality
- `GET /health` - Health check
- `POST /upload_pdf` - Upload PDF documents (protected)
- `POST /ask` - Ask questions to the RAG system (protected)

### Example API Usage

```bash
# Sign up
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"SecurePass123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123"}'

# Ask a question (with token)
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query":"What is MeTTa?"}'
```

## 🔧 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Required
GEMINI_API_KEY=your_actual_api_key_here

# Database
DATABASE_URL=sqlite:///./data/users.db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Optional: RAG Configuration
GENERATION_MODEL=gemini-2.0-flash
CHROMA_DB_DIR=./data/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=6
MAX_REWRITE_ATTEMPTS=2
MAX_REFINEMENT_ROUNDS=2
CRITIQUE_CONFIDENCE_THRESHOLD=0.9
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
PORT=5000
```

### Frontend Configuration

Update `frontend/src/app/constants.js` for production:

```javascript
// Change these URLs for production deployment
export const CHAT_API_URL = "http://your-backend-url/ask";
export const SIGNUP_API_URL = "http://your-backend-url/auth/signup";
export const LOGIN_API_URL = "http://your-backend-url/auth/login";
```

## 🧠 How the Self-Reflection Works

The system implements a sophisticated multi-stage reasoning process:

1. **🔍 Document Retrieval** - Finds relevant document chunks using semantic search
2. **✅ Relevance Check (ISREL)** - Evaluates if retrieved documents are actually relevant
3. **🔄 Query Rewriting** - If documents aren't relevant, automatically rewrites the query
4. **💡 Answer Generation** - Creates an initial answer based on retrieved context
5. **🛡️ Factuality Check (ISSUP)** - Critiques whether the answer is fully supported by sources
6. **✨ Usefulness Check (ISUSE)** - Evaluates if the answer is helpful and addresses the question
7. **🔧 Answer Refinement** - If critiques fail, refines the answer using feedback
8. **🎯 Guided Re-retrieval** - Optionally retrieves additional documents if missing information

Each step is logged and visualized in the frontend, providing complete transparency into the AI's reasoning process.

## 🛠️ Development

### Backend Development

```bash
cd backend
.venv\Scripts\activate  # Activate virtual environment
python app.py           # Start development server
```

### Frontend Development

```bash
cd frontend
npm run dev            # Start development server
npm run build          # Build for production
npm start              # Start production server
```

### Database Management

```bash
cd backend
python init_db.py      # Initialize database tables
```

## 🧪 Testing

### Backend Testing

Use the provided Postman collection or test with curl:

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test signup
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"TestPass123"}'
```

### Frontend Testing

1. **Open** `http://localhost:3000`
2. **Sign up** for a new account
3. **Login** with your credentials
5. **Ask questions** about the document content

## 📦 Dependencies

### Backend Dependencies
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **PyJWT** - JWT token handling
- **bcrypt** - Password hashing
- **ChromaDB** - Vector database
- **LangChain** - Text processing
- **Google Gemini** - Language model
- **Sentence Transformers** - Embeddings

### Frontend Dependencies
- **Next.js** - React framework
- **React 19** - UI library
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## 🚀 Deployment

### Backend Deployment

1. **Set up a production server** (AWS, DigitalOcean, etc.)
2. **Install Python and dependencies**
3. **Set environment variables** for production
4. **Use a production WSGI server** like Gunicorn
5. **Set up a reverse proxy** with Nginx

### Frontend Deployment

1. **Build the application**: `npm run build`
2. **Deploy to Vercel, Netlify, or similar**
3. **Update API URLs** in constants.js
4. **Configure environment variables**

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini** for advanced language processing capabilities
- **ChromaDB** for efficient vector storage
- **LangChain** for text processing utilities
- **MeTTa** community for the documentation

## 📞 Support

If you encounter any issues or have questions:

1. **Check the logs** in both backend and frontend consoles
2. **Verify environment variables** are set correctly
3. **Ensure all dependencies** are installed
4. **Check API connectivity** between frontend and backend

For additional help, please open an issue in the repository.

---

**Built with ❤️ for the MeTTa community**
