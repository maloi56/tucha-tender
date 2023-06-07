from app import create_app, config, db, initial_create

app = create_app(config.test_config)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        initial_create()
        app.run()
