# Contributing to ZehraGuard InsightX

## 📋 Project Notice

**⚠️ This is a demo project.** ZehraGuard InsightX is provided as a demonstration of AI-powered insider threat detection capabilities. For the complete commercial solution, full implementation, enterprise support, or professional services, please contact ZehraSec or Yashab Alam directly.

### 🏢 Full Project & Commercial Inquiries
- **Company**: ZehraSec
- **Creator**: Yashab Alam
- **Website**: [www.zehrasec.com](https://www.zehrasec.com)
- **Contact**: yashabalam707@gmail.com
- **Services**: Complete solution, enterprise implementation, custom development, training, and support

---

First off, thank you for considering contributing to ZehraGuard InsightX! 🎉 It's people like you that make ZehraGuard InsightX such a great tool for insider threat detection and prevention.

## 🌟 Quick Links

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [License](LICENSE)
- [Donation Information](DONATE.md)

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

```bash
# Required
docker --version          # Docker 20.10+
docker-compose --version  # Docker Compose 2.0+
python --version          # Python 3.9+
node --version           # Node.js 16+
git --version            # Git 2.30+

# Optional but recommended
make --version           # Make for build automation
```

### Development Setup

1. **Fork the repository**
   ```bash
   # Go to https://github.com/yashab-cyber/zehraguard and click Fork
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/zehraguard.git
   cd zehraguard
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/yashab-cyber/zehraguard.git
   ```

4. **Set up development environment**
   ```bash
   # Copy environment configuration
   cp .env.example .env
   
   # Start development services
   docker-compose -f docker-compose.dev.yml up -d
   
   # Install Python dependencies
   pip install -r requirements-dev.txt
   
   # Install Node.js dependencies
   cd dashboard && npm install
   ```

5. **Verify setup**
   ```bash
   # Run tests
   make test
   
   # Check code formatting
   make lint
   ```

## 🤝 How to Contribute

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

**Great Bug Reports** include:

- **Summary**: Clear, descriptive title
- **Environment**: OS, Python version, Docker version
- **Steps to reproduce**: Detailed steps to trigger the bug
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Screenshots**: If applicable
- **Logs**: Relevant error messages or logs

### 💡 Suggesting Features

We love feature suggestions! Please:

1. **Check existing issues** for similar suggestions
2. **Describe the problem** your feature would solve
3. **Explain your solution** in detail
4. **Consider alternatives** you've thought about
5. **Provide use cases** and examples

### 🔧 Code Contributions

We welcome contributions in several areas:

#### 🧠 AI & Machine Learning
- Behavioral analysis algorithms
- Anomaly detection models
- Risk scoring improvements
- Model optimization

#### 🖥️ Frontend Development
- Dashboard improvements
- New visualizations
- User experience enhancements
- Mobile responsiveness

#### ⚡ Backend Development
- API enhancements
- Performance optimizations
- Database improvements
- Integration features

#### 🔗 Integrations
- SIEM platform connectors
- Cloud service integrations
- Authentication providers
- Third-party security tools

#### 📚 Documentation
- Code documentation
- User guides
- API documentation
- Tutorial content

## 🔄 Pull Request Process

### 1. **Create a feature branch**
```bash
git checkout -b feature/amazing-new-feature
```

### 2. **Make your changes**
- Follow our [coding standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. **Commit your changes**
```bash
# Use conventional commit format
git commit -m "feat: add behavioral pattern analysis

- Implement new ML algorithm for pattern detection
- Add unit tests for pattern analyzer
- Update API documentation"
```

### 4. **Push to your fork**
```bash
git push origin feature/amazing-new-feature
```

### 5. **Create a Pull Request**

**Great Pull Requests** include:

- **Clear title** describing the change
- **Detailed description** of what and why
- **Link to related issues** (if applicable)
- **Screenshots** for UI changes
- **Testing instructions** for reviewers
- **Breaking changes** clearly marked

### 6. **Review Process**

- Automated tests must pass
- Code review by maintainers
- Address feedback promptly
- Maintain clean commit history

## 📏 Coding Standards

### Python Code Style
```python
# Use Black for formatting
black .

# Use isort for imports
isort .

# Use flake8 for linting
flake8 .

# Use mypy for type checking
mypy .
```

### TypeScript/React Code Style
```bash
# Use Prettier for formatting
npm run format

# Use ESLint for linting
npm run lint

# Use TypeScript compiler
npm run type-check
```

### General Guidelines

- **Variable naming**: Use descriptive names
- **Function naming**: Use verbs that describe the action
- **Class naming**: Use PascalCase
- **Constants**: Use UPPER_SNAKE_CASE
- **Comments**: Explain "why", not "what"
- **Documentation**: Use docstrings for all public functions

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-unit        # Unit tests
make test-integration # Integration tests
make test-e2e        # End-to-end tests

# Run tests with coverage
make test-coverage
```

### Writing Tests

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **E2E tests**: Test complete user workflows
- **Aim for 80%+ coverage** on new code
- **Use meaningful test names** that describe behavior

### Test Structure
```python
def test_behavioral_analyzer_detects_anomaly():
    # Arrange
    analyzer = BehavioralAnalyzer()
    normal_data = create_normal_behavior_data()
    anomalous_data = create_anomalous_behavior_data()
    
    # Act
    result = analyzer.analyze(anomalous_data)
    
    # Assert
    assert result.is_anomaly is True
    assert result.risk_score > 0.7
```

## 📖 Documentation

### Code Documentation
- Use clear, descriptive docstrings
- Include parameter and return type information
- Provide usage examples for complex functions

### User Documentation
- Keep README.md updated
- Add new features to documentation
- Include screenshots for UI changes
- Provide clear installation/setup instructions

## 💬 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: yashabalam707@gmail.com for direct contact
- **Social Media**: Follow [@zehrasec](https://x.com/zehrasec) for updates

### Getting Help

- Check existing documentation
- Search GitHub issues
- Ask in GitHub Discussions
- Contact maintainers directly

### Mentorship

New to open source? We're here to help!

- Look for issues labeled `good first issue`
- Ask questions in GitHub Discussions
- Request code review guidance
- Pair programming sessions available

## 🏆 Recognition

We believe in recognizing contributors:

- **Contributors list** in README.md
- **Commit attribution** preserved
- **Special mentions** in release notes
- **Swag and merchandise** for significant contributions
- **Beta access** to new features

## 📋 Contributor Agreement

By contributing to ZehraGuard InsightX, you agree that:

- Your contributions will be licensed under the MIT License
- You have the right to submit your contributions
- You grant us the right to use your contributions
- You will follow our Code of Conduct

## 🔄 Development Workflow

### Branch Naming Convention
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Message Convention
```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

## 📞 Contact

**Project Maintainer**: Yashab Alam  
**Email**: yashabalam707@gmail.com  
**GitHub**: [@yashab-cyber](https://github.com/yashab-cyber)  
**Company**: ZehraSec  
**Website**: [www.zehrasec.com](https://www.zehrasec.com)

## 🙏 Thank You

Every contribution, no matter how small, makes a difference. Thank you for helping make ZehraGuard InsightX better for everyone!

---

**Last Updated**: July 25, 2025  
**Version**: 1.0

---

**🛡️ Made with ❤️ by Yashab Alam (Founder of ZehraSec) and the ZehraGuard development team**
