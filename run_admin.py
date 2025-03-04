from admin import create_app, create_admin

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Создаем первого администратора при первом запуске
        create_admin('admin', 'admin123')  # Измените пароль на более безопасный
    
    app.run(host='0.0.0.0', port=5000, debug=True) 