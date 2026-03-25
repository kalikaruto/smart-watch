
import npyscreen
from config import load_cameras, save_cameras

class CameraListForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Cameras (A: Add, E: Edit, D: Delete, Q: Quit)", editable=False)
        self.camera_list = self.add(npyscreen.SelectOne, max_height=10, scroll_exit=True)
        self.update_list()

        self.add_handlers({
            "a": self.add_camera,
            "e": self.edit_camera,
            "d": self.delete_camera,
            "q": self.quit_app
        })

    def update_list(self):
        self.parentApp.cameras = load_cameras()
        self.camera_list.values = [f"{cam['name']}" for cam in self.parentApp.cameras]
        self.camera_list.display()

    def add_camera(self, *args):
        self.parentApp.getForm('EDIT').index = None
        self.parentApp.switchForm('EDIT')

    def edit_camera(self, *args):
        if self.camera_list.value:
            self.parentApp.getForm('EDIT').index = self.camera_list.value[0]
            self.parentApp.switchForm('EDIT')

    def delete_camera(self, *args):
        if self.camera_list.value:
            idx = self.camera_list.value[0]
            del self.parentApp.cameras[idx]
            save_cameras(self.parentApp.cameras)
            self.update_list()

    def quit_app(self, *args):
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

class EditCameraForm(npyscreen.ActionForm):
    def create(self):
        self.name = self.add(npyscreen.TitleText, name="Name:")
        self.link = self.add(npyscreen.TitleText, name="Link:")
        self.description = self.add(npyscreen.TitleText, name="Description:")
        self.index = None

    def beforeEditing(self):
        if self.index is not None:
            cam = self.parentApp.cameras[self.index]
            self.name.value = cam.get("name", "")
            self.link.value = cam.get("link", "")
            self.description.value = cam.get("desc", "")
        else:
            self.name.value = ""
            self.link.value = ""
            self.description.value = ""

    def on_ok(self):
        if not all([self.name.value, self.link.value, self.description.value]):
            npyscreen.notify_confirm("All fields are required!", title="Error")
            return

        new_data = {
            "name": self.name.value,
            "link": self.link.value,
            "desc": self.description.value
        }

        if self.index is not None:
            self.parentApp.cameras[self.index] = new_data
        else:
            self.parentApp.cameras.append(new_data)

        save_cameras(self.parentApp.cameras)
        self.parentApp.getForm("MAIN").update_list()
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        self.parentApp.switchForm("MAIN")

class CameraApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.cameras = load_cameras()
        self.addForm("MAIN", CameraListForm, name="Camera Manager")
        self.addForm("EDIT", EditCameraForm, name="Edit Camera")

if __name__ == "__main__":
    app = CameraApp()
    app.run()
