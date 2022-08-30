import arcpy
class LAS_Base:
    """ Base Class to support data abstraction and common methods
        - Inheritance   to inherit from single-parent (base class)
        - Encapsulation to bind all shared attribute to a single unit - self
        - Polymorphism  to defines common methods in this parent class e.g greeting
    """

    def __init__(self):
        self.path = "C:Path"
        self.workspace = "C:Workspace"

    def get_info(self):
        arcpy.CheckOutExtension("3D")
        desc = arcpy.Describe(f"FilePath")

class Building:
    """ Handle Building Extraction - Support LAS-> Multipatch | TIN -> Multipatch"""

    def __init__(self, user):
        print("Extracting Building")
        LAS_Base.__init__(self)                 # Inherit Base Class
        LAS_Base.get_info(self)                 # Use common method
        new_path = self.path + "/newFolder"     # Use inherited attr
        print(new_path)
        self.user = user

    def data_prep(self):
        """Filter LAS Class"""
        pass

    def sanitize(self):
        """Re-Classify building & Ground, Remove noise"""
        pass

    def remove_gap():
        """Remove overlapped gap Class 6 -- Class2"""
        pass

    def todo():
        pass

    def __str__(self):
        return "Workflow + This is how to"

class Roof:
    def __init__(self):
        print("Extracting Roof")

class Roof_Segment:
    def __init__(self):
        print("Segmenting Roof")

class Tree:
    def __init__(self):
        print("Extracting Tree")


bla = Building("Edward")
print(bla)
