from application import Application

# Unsafe decorator pattern implemented
# An instance of this class is made when an unsafe application is used.


class UnsafeDecorator(Application):
    def __init__(self, app):
        self.app = app

    # Executes the command and prints the error if an error is raised.
    def exec(self, args, output):
        try:
            self.app.exec(args, output)
        except Exception as e:
            print(e)
