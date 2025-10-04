# Event Manager Platform

A comprehensive event management system built with Django, featuring real-time communication, multi-role user management, and integrated payment processing.

## Features

### Authentication & User Management
- Multi-role system (Users, Managers, Admins)
- Secure authentication with email verification
- Profile management with avatar uploads
- OTP verification system

### Event Management
- Complete event lifecycle management
- Event creation, editing, and deletion
- Event registration and ticketing
- Venue booking and management
- Event categories and filtering
- Image gallery and media management

### Communication & Collaboration
- Real-time chat rooms
- Team collaboration tools
- Announcement system
- Direct messaging
- Email notifications

### AI-Powered Features
- AI Chatbot for customer support
- AI Mood Designer for event themes
- Smart recommendations
- Automated responses

### Payment & Ticketing
- Secure payment processing
- Multiple payment methods
- Ticket generation and management
- Refund handling

### Analytics & Reporting
- Event statistics and insights
- User engagement metrics
- Revenue tracking
- Performance analytics

### Modern UI/UX
- Responsive design
- Dark/Light theme support
- Mobile-optimized interface
- Professional dashboard layouts

## Quick Start

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL (recommended)
- Redis (for real-time features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Meet-1409/Event-Management-Platform.git
   cd Event-Management-Platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API keys
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Login with your superuser credentials

## Technology Stack

- **Backend:** Django 4.0+, Python 3.8+
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Database:** PostgreSQL, SQLite (development)
- **Real-time:** WebSockets, Redis
- **AI Integration:** OpenAI API, Custom AI models
- **Payment:** Stripe, PayPal integration
- **Deployment:** Docker, Heroku, AWS

## User Roles

### Regular Users
- Browse and register for events
- Manage personal profile
- Access event galleries
- Use AI chatbot support

### Managers
- Create and manage events
- Handle venue bookings
- Manage team communications
- Access analytics dashboard

### Administrators
- Full system access
- User management
- System configuration
- Advanced analytics

## Configuration

### Environment Variables
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/eventmanager
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-key
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

### Database Configuration
The application supports multiple databases:
- **PostgreSQL** (production)
- **SQLite** (development)
- **MySQL** (alternative)

## Performance Features

- Database query optimization
- Caching with Redis
- Image compression and optimization
- CDN integration for static files
- Lazy loading for better performance

## Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing
- Rate limiting
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Meet Sutariya**
- GitHub: [@Meet-1409](https://github.com/Meet-1409)
- Email: meetsutariya@gmail.com

## Acknowledgments

- Django community for excellent documentation
- Bootstrap team for the UI framework
- OpenAI for AI integration capabilities
- All contributors and testers

## Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Contact me via email
- Check the documentation