from app import create_app, config, db, initial_create

if __name__ == "__main__":
    app = create_app(config.dev_config)
    with app.app_context():
        db.create_all()
        initial_create()
        app.run()
