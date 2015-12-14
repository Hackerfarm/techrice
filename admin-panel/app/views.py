from flask import render_template
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder import ModelView
from app import appbuilder, db

"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""

"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()

from models import Site, Node, Sensor, SensorType, NodeType, Reading

class SiteModelView(ModelView):
	datamodel = SQLAInterface(Site)
	search_columns = ['id', 'alias']	
	# label_columns = {'contact_group':'Contacts Group'}
	list_columns = ['id', 'alias']

	# expanded = False
	# show_fieldsets = [
	# 	('Info',{'fields':['id','alias', 'nodes']}),
	# 	# ('Personal Info',{'fields':['alias'],'expanded':False}),
	# ]

appbuilder.add_view(SiteModelView, "Sites",icon = "fa-car",category = "Resources")


class NodeModelView(ModelView):
	datamodel = SQLAInterface(Node)
	search_columns = ['id', 'alias']	
	# label_columns = {'contact_group':'Contacts Group'}
	list_columns = ['id', 'alias', 'site_id', 'latitude', 'longitude', 'created', 'updated']
	# expanded = False
	# show_fieldsets = [
	# 	('Info',{'fields':['id','alias','site_id']}),
	# 	# ('Personal Info',{'fields':['alias'],'expanded':False}),
	# ]

appbuilder.add_view(NodeModelView, "Nodes",icon = "fa-site",category = "Resources")

# class NodetypeModelView(ModelView):
# 	datamodel = SQLAInterface(NodeType)
# 	search_columns = ['id', 'alias']	
# 	list_columns = ['id', 'alias', 'sensortype_id', 'node_id', 'created', 'updated']

# appbuilder.add_view(NodetypeModelView, "Sensors",icon = "fa-site",category = "Resources")


class SensorModelView(ModelView):
	datamodel = SQLAInterface(Sensor)
	search_columns = ['id', 'alias']	
	list_columns = ['id', 'alias', 'sensortype_id', 'node_id', 'created', 'updated']

appbuilder.add_view(SensorModelView, "Sensors",icon = "fa-site",category = "Resources")



# class SensorModelView(ModelView):
# 	datamodel = SQLAInterface(Sensor)
# 	search_columns = ['id', 'alias']	
# 	list_columns = ['id', 'alias', 'sensortype_id', 'node_id', 'created', 'updated']

# appbuilder.add_view(SensorModelView, "Sensors",icon = "fa-site",category = "Resources")


# class NodeModelView(ModelView):
# 	datamodel = SQLAInterface(Node)
# 	search_columns = ['id', 'alias']	
# 	# label_columns = {'contact_group':'Contacts Group'}
# 	list_columns = ['id', 'alias']
# 	# expanded = False
# 	# show_fieldsets = [
# 	# 	('Info',{'fields':['id','alias','site_id']}),
# 	# 	# ('Personal Info',{'fields':['alias'],'expanded':False}),
# 	# ]

# appbuilder.add_view(NodeModelView, "Nodes",icon = "fa-site",category = "Resources")

# class NodeModelView(ModelView):
# 	datamodel = SQLAInterface(Node)
# 	search_columns = ['id', 'alias']	
# 	# label_columns = {'contact_group':'Contacts Group'}
# 	list_columns = ['id', 'alias']
# 	# expanded = False
# 	# show_fieldsets = [
# 	# 	('Info',{'fields':['id','alias','site_id']}),
# 	# 	# ('Personal Info',{'fields':['alias'],'expanded':False}),
# 	# ]

# appbuilder.add_view(NodeModelView, "Nodes",icon = "fa-site",category = "Resources")



