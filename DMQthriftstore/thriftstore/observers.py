class Observer:
    def update(self, subject):
        pass

class ItemSoldNotifier(Observer):
    def update(self, item):
        print(f"Notification: '{item.title}' has been sold.")
       
