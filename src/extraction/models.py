class Author():
    name = None
    github = None
    blog = None
    location = None
    projects = []
    dataline =""

    def __str__(self):
        return dataline
    
    def add_project(self, project):
        self.projects.append(project)

    def __init__(self):
        pass

class Project():
    name = None
    url = None
    description = None
    more_info = None
    date = None
    dataline =""



    def __str__(self):
        return name
    
    def __init__(self):
        pass

    # def __init__(self, name, url, description, more_info, date):
    #     self.name = name
    #     self.url = url
    #     self.description = description
    #     self.more_info = more_info
    #     self.date = date


    
    