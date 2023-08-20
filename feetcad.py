"""
Simple example showing some animated shapes
"""
import math
import pyglet
from pyglet import shapes
import json
from pyglet.graphics import Group
from pyglet.math import Vec2
import time
import pyglet.gl as gl
from tkinter import Tk, Frame, Menu

class CameraGroup(Group):
    """ Graphics group emulating the behaviour of a camera in 2D space. """

    def __init__(self, window, x, y, zoom=1.0, order=0, parent=None):
        super().__init__(order, parent)
        self._window = window
        self.x = x
        self.y = y
        self.zoom = zoom

    @property
    def position(self) -> Vec2:
        """Query the current offset."""
        return Vec2(self.x, self.y)

    @position.setter
    def position(self, new_position: Vec2):
        """Set the scroll offset directly."""
        self.x, self.y = new_position

    def set_state(self):
        """ Apply zoom and camera offset to view matrix. """

        # Translate using the offset.
        view_matrix = self._window.view.translate((-self.x * self.zoom, -self.y * self.zoom, 0))
        # Scale by zoom level.
        view_matrix = view_matrix.scale((self.zoom, self.zoom, 1))

        self._window.view = view_matrix

    def unset_state(self):
        """ Revert zoom and camera offset from view matrix. """
        # Since this is a matrix, you will need to reverse the translate after rendering otherwise
        # it will multiply the current offset every draw update pushing it further and further away.

        # Use inverse zoom to reverse zoom
        view_matrix = self._window.view.scale((1 / self.zoom, 1 / self.zoom, 1))
        # Reverse translate.
        view_matrix = view_matrix.translate((self.x * self.zoom, self.y * self.zoom, 0))

        self._window.view = view_matrix

    def set_zoom(self, zoom):
        self.zoom = zoom

    def set_pos(self, x, y):
        self.x = x
        self.y = y


class CenteredCameraGroup(CameraGroup):
    """ Alternative centered camera group.

    (0, 0) will be the center of the screen, as opposed to the bottom left.
    """

    def set_state(self):
        # Translate almost the same as normal, but add the center offset
        x = -self._window.width // 2 / self.zoom + self.x
        y = -self._window.height // 2 / self.zoom + self.y

        view_matrix = self._window.view.translate((-x * self.zoom, -y * self.zoom, 0))
        view_matrix = view_matrix.scale((self.zoom, self.zoom, 1))
        self._window.view = view_matrix

    def unset_state(self):

        x = -self._window.width // 2 / self.zoom + self.x
        y = -self._window.height // 2 / self.zoom + self.y

        view_matrix = self._window.view.scale((1 / self.zoom, 1 / self.zoom, 1))
        view_matrix = view_matrix.translate((x * self.zoom, y * self.zoom, 0))
        self._window.view = view_matrix

    def set_zoom(self, zoom):
        self.zoom = zoom

    def set_pos(self, x, y):
        self.x = x
        self.y = y

class LIBRARY:

    def __init__(self):
       self.__json_data = None
       self.__file_name = 'library.json'

    def setLibraryFile(self,fileName):
        self.__file_name = fileName

    def loadLibrary(self):
        with open(__file_name, 'r') as handle:
            self.__json_data = json.load(handle)

    def saveLibrary(self):
        with open(__file_name, 'w') as f:
            f.write(json.dumps(self.__json_data, indent=4))


class SCHEME_DRAW_ITEM:
    def __init__(self,shape=None):
        self.shapes = [shape] if shape != None else []

    def addItem(self,item):
        self.shapes.append(item)

    def clear(self):
        self.shapes = []

class SCHEME:

    def __init__(self):
        self.__components=[]
        self.__fileName = None
        self.jsonData = None

    def loadScheme(self,fileName):
        self.__fileName = fileName
        with open(fileName, 'r') as handle:
            self.jsonData = json.load(handle)

    def saveScheme(self,fileName = ""):
        if fileName != "":
            self.__fileName = fileName
        #print(json.dumps(self.jsonData, indent=4,default=bool))
        with open(self.__fileName, 'w') as f:
            f.write(json.dumps(self.jsonData, indent=4, default=bool))

class HUD():

    class BUTTON():
        def __init__(self, owner_window, image, batch, camera, function, x, y):
            self.owner_window = owner_window
            self.batch = batch
            self.camera = camera
            self.function = function

            #pyglet.resource.path = ['buttons']
            #pyglet.resource.reindex()

            self.image = pyglet.resource.image(image)
            self.sprite = pyglet.sprite.Sprite(self.image,
                                  x=x,
                                  y=y,
                                  batch = self.batch,
                                  group = self.camera)
            self.sprite.opacity = 128
            self.sprite.anchor_x = self.sprite.image.width/2
            self.sprite.visible = False




    def __init__(self, owner_window, batch, camera):
        self.buttons = []
        self.batch = batch
        self.camera = camera
        self.owner_window = owner_window
        self.width = 0
        self.height = 0

    def add_button(self, image, function):
        x = 0
        for button in self.buttons:
            x+=button.image.width
        button = HUD.BUTTON(self.owner_window, image, self.batch, self.camera, function, x, 0)

        self.width+=button.image.width
        if self.height < button.image.height:
            self.height = button.image.height

        self.buttons.append(button)

    def recalculate_hud(self, window_width, window_height, mouse_x, mouse_y):
        def in_rect(x0,y0,x1,y1,x2,y2):
            return x0>=x1 and x0<=x2 and y0>=y1 and y0<=y2

        x0 = -(window_width - self.width - 40) * mouse_x / window_width -20

        x = 0
        for button in self.buttons:
            button.sprite.x = x - x0
            #button.sprite.update()
            if in_rect(mouse_x, mouse_y, button.sprite.x,button.sprite.y,button.sprite.x+button.image.width,button.sprite.y+button.image.height):
                button.sprite.scale = 1.1
                button.sprite.opacity = 255
                button.sprite.color = (255,255,255)
            else:
                button.sprite.scale = 1
                button.sprite.opacity = 128
                button.sprite.color = (200,200,200)

            x+=button.sprite.width


    def set_visible(self,visible):
        for button in self.buttons:
            button.sprite.visible = visible

class FEETCAD(pyglet.window.Window):

    def __init__(self):
        config = pyglet.gl.Config()
        config.sample_buffers = 1
        config.samples = 1
        super(FEETCAD,self).__init__(720, 480, "FEETCAD",config=config,resizable=True,style=pyglet.window.Window.WINDOW_STYLE_DEFAULT)
        self.time = 0
        self.__grid_batch = pyglet.graphics.Batch()
        self.circle = shapes.Circle(360, 240, 75, color=(255, 225, 255, 250))
        self.scheme = SCHEME()
        self.batch = pyglet.graphics.Batch()
        self.camera = CenteredCameraGroup(self,0,0,1)
        self.camera_hud = CameraGroup(self,0,0,1)
        self.__clickTime = time.time()

        self.__grid_shapes_big = []
        self.__grid_shapes_small = []

        self.__grid_visible = False
        self.__last_grid_state = True

        self.magnifier = 10.0

        self.grid_width = 2
        self.grid_step = 1
        self.grid_steps = 60
        self.grid_min_cell_width = 20
        self.grid_zoom_step = 10
        self.grid_zero_color = color=(255,255,255,150)
        self.grid_primary_color = color=(255,255,255,100)
        self.grid_middle_color = color=(255,255,255,50)
        self.grid_secondary_color = color=(255,255,255,25)

        self.under_mouse_shapes = []

        self.zoom_step = 5
        self.cursor = shapes.Circle(20, 20, 2, color=(255,255,255,50), batch = self.batch, group = self.camera)


        self.generate_grid()

        self.hilighted_components = []

        self.in_macro_edit = None

        self.miny,self.minx,self.maxy,self.maxx = (100,100,-100,-100)

        self.toggle_grid()

        self.clearScheme()

        self.borders_color = (171,0,247,150)
        self.border_dots_width = 0.5 * self.magnifier


        self.hud_macro = HUD(self, self.batch, self.camera_hud)
        self.hud_macro.add_button('buttons/macro_line.png',self.do_macro_create_line())
        self.hud_macro.add_button('buttons/macro_text.png',self.do_macro_create_line())
        self.hud_macro.add_button('buttons/macro_pin.png',self.do_macro_create_line())
        self.hud_macro.add_button('buttons/macro_rectangle.png',self.do_macro_create_line())
        self.hud_macro.add_button('buttons/macro_circle.png',self.do_macro_create_line())
        self.hud_macro.add_button('buttons/macro_from_file.png',self.do_macro_create_line())
        self.hud_macro.add_button('buttons/macro_to_file.png',self.do_macro_create_line())
        self.hud_macro.add_button('buttons/macro_from_db.png',self.do_macro_create_line())
        for j in range(8):

            self.hud_macro.add_button('buttons/macro_line.png',self.do_macro_create_line())



        self.fps = pyglet.window.FPSDisplay(window=self)

    def do_macro_create_line(self):
        pass



    def check_for_macro_edit(self, enter_to_edit = True):
        if enter_to_edit:
            if len(self.hilighted_components) == 1:
                self.in_macro_edit = self.hilighted_components[0]

                if 'components' in self.scheme.jsonData:
                    for component in self.scheme.jsonData['components']:

                        for shape in component['temp_shapes'].shapes:
                            color = shape.color
                            if len(color) == 4:
                                shape.color = (color[0],color[1],color[2],20)

                self.hud_macro.set_visible(True)
                self.loadShapesFromJson(self.hilighted_components[0],macro_mode = True)
                print("self.in_macro_edit['x'],self.in_macro_edit[y]",self.in_macro_edit['x'],self.in_macro_edit['y'])
        else:
            print('exiting macro edit')
            self.in_macro_edit = None
            self.loadShapesFromJson()
            self.hud_macro.set_visible(False)

        for shape in self.in_macro_edit_shapes:
            shape.visible = self.in_macro_edit != None

        self.recalculate_grid()

    def generate_grid(self):
        vert = []
        horz = []
        for x in range(0,self.grid_steps):
            grid_line = shapes.Rectangle(x*self.grid_step, -200000, self.grid_width, 400000,  color=(255,255,255,50), batch = self.batch, group = self.camera)
            vert.append(grid_line)
        for y in range(0,self.grid_steps):
            grid_line = shapes.Rectangle(-200000, y*self.grid_step, 400000, self.grid_width,  color=(255,255,255,50), batch = self.batch, group = self.camera)
            horz.append(grid_line)

        self.__grid_shapes_big.append(horz)
        self.__grid_shapes_big.append(vert)
        print(self.__grid_shapes_big)

    def recalculate_grid(self):
        if not self.__last_grid_state and not self.__grid_visible:
            return

        newx = self.camera.x
        newy = self.camera.y

        cell_width = self.grid_step*self.camera.zoom/self.magnifier
        #print('cell width',cell_width)
        #normal: between 10 and 100
        zoom_factor = 1
        cnt = 1

        while cell_width < self.grid_min_cell_width:
            zoom_factor = zoom_factor*self.grid_zoom_step
            cell_width = self.grid_step*self.camera.zoom*zoom_factor

        cell_width = self.grid_step*self.camera.zoom*zoom_factor
        #print('zoom_factor',zoom_factor)
        #print('new cell width',cell_width)

        middlex = (self.grid_steps*self.grid_step*zoom_factor)/2
        if self.in_macro_edit != None:
            middlex+=self.in_macro_edit['x']*self.magnifier

        middley = (self.grid_steps*self.grid_step*zoom_factor)/2
        if self.in_macro_edit != None:
            middley+=self.in_macro_edit['y']*self.magnifier

        #vertical lines
        x = 0
        for line in self.__grid_shapes_big[1]:
            line.x = x*self.grid_step*zoom_factor-middlex+self.camera.x-self.camera.x%(zoom_factor*self.grid_step)

            if line.x  == 0:
                line.color = self.grid_zero_color
            elif line.x % (self.grid_zoom_step*zoom_factor) == 0:
                line.color = self.grid_primary_color
            elif line.x % (self.grid_zoom_step/2*zoom_factor) == 0:
                line.color = self.grid_middle_color
            else:
                line.color = self.grid_secondary_color

            line.width = self.grid_width/self.camera.zoom
            line.x-=line.width/2
            if self.in_macro_edit != None:
                line.x+=self.in_macro_edit['x']*self.magnifier


            x+=1

            if not self.__grid_visible:
                line.x+=1000000

        #horizontal lines
        y = 0
        for line in self.__grid_shapes_big[0]:
            line.y = y*self.grid_step*zoom_factor-middley+self.camera.y-self.camera.y%(zoom_factor*self.grid_step)

            if line.y  == 0:
                line.color = self.grid_zero_color
            elif line.y % (self.grid_zoom_step*zoom_factor) == 0:
                line.color = self.grid_primary_color
            elif line.y % (self.grid_zoom_step/2*zoom_factor) == 0:
                line.color = self.grid_middle_color
            else:
                line.color = self.grid_secondary_color

            line.height = self.grid_width/self.camera.zoom
            line.y-=line.height/2
            if self.in_macro_edit != None:
                line.y+=self.in_macro_edit['y']*self.magnifier

            y+=1

            if not self.__grid_visible:
                line.y+=1000000

        self.__last_grid_state = self.__grid_visible

        #print('grid_recalculate after','newx newy',newx,newy)
        #0.8 and 8




    def toggle_grid(self):
        self.__grid_visible = not self.__grid_visible
        self.recalculate_grid()
        print('grid',self.__grid_visible)

    def redraw(self):
        self.clearScheme()
        self.loadShapesFromJson()

    def reset_view(self):
        #calc zoom
        #WITH BORDER 20PX

        maxx = self.maxx
        minx = self.minx
        maxy = self.maxy
        miny = self.miny

        if self.in_macro_edit != None:
            minx,miny,maxx,maxy = self.loadShapesFromJson(self.in_macro_edit, onlyBounds = True)

        scheme_width = maxx - minx+20
        scheme_height = maxy - miny+20
        max_dim_scheme, max_dim_window = (0, 0)

        if scheme_width > scheme_height:
            max_dim_scheme = scheme_width
            max_dim_window = self.width
        else:
            max_dim_scheme = scheme_height
            max_dim_window = self.height

        zoom = max_dim_window/max_dim_scheme
        self.camera.zoom=zoom
        self.camera.x = minx+(maxx-minx)/2
        self.camera.y = miny+(maxy-miny)/2
        self.recalculate_grid()

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor.x = (-self.width/2+x)/self.camera.zoom+self.camera.x
        self.cursor.y = (-self.height/2+y)/self.camera.zoom+self.camera.y
        #print("mouse on canvas: x,y:",self.cursor.x,self.cursor.y)
        #print('len(self.hilighted_components)',len(self.hilighted_components));
        if self.in_macro_edit == None:
            selected = self.check_mouse_onshape(self.cursor.x, self.cursor.y)
            #print(selected)

            for component in self.hilighted_components:
                #print('last',component['name'])
                self.loadShapesFromJson(component)

            if len(selected) > 0:
                for component in selected:
                    #print('new',selected)
                    for shape in component['temp_shapes'].shapes:
                        shape.color = [255,0,0,255]

            self.hilighted_components = selected
        else:
            self.hud_macro.recalculate_hud(self.width, self.height, x, y)



    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        dx = (self.width/2-x)
        dy = (self.height/2-y)
        print('dx,dy',dx,dy)

        if scroll_y > 0:
            #dx = (self.width/2-x)/self.camera.zoom)
            newzoom = self.camera.zoom + self.camera.zoom/self.zoom_step
            self.camera.zoom=newzoom

            dx = (dx/newzoom)/self.zoom_step
            dy = (dy/newzoom)/self.zoom_step
            #print('dx',dx)
            self.camera.x -= dx
            self.camera.y -= dy

        else:
            #dx = (self.width/2-x)/self.camera.zoom)
            newzoom = self.camera.zoom - self.camera.zoom/self.zoom_step
            self.camera.zoom=newzoom

            dx = (dx/newzoom)/self.zoom_step
            dy = (dy/newzoom)/self.zoom_step
            #print('dx',dx)
            self.camera.x += dx
            self.camera.y += dy


        self.recalculate_grid()

        #self.camera.y -= dy/self.camera.zoom
        print('scroll self.camera.zoom,scroll_y',self.camera.zoom,scroll_y)


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button == pyglet.window.mouse.MIDDLE:
            self.camera.x -= dx/self.camera.zoom
            self.camera.y -= dy/self.camera.zoom
            self.recalculate_grid()
            print('drag self.camera.zoom,self.camera.x,self.camera.y',self.camera.zoom,self.camera.x,self.camera.y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.MIDDLE:
            t = time.time()
            if t - self.__clickTime < 0.25:
                self.reset_view()
            else:
                self.__clickTime = time.time()

        if button == pyglet.window.mouse.LEFT:
            t = time.time()
            if t - self.__clickTime < 0.25:
                self.check_for_macro_edit()
            else:
                self.__clickTime = time.time()

    def recalculate_in_macro_label(self):
        if len(self.in_macro_edit_shapes) >= 2:
            self.in_macro_edit_shapes[0].x = self.width - 80
            self.in_macro_edit_shapes[0].y = self.height - 20
            self.in_macro_edit_shapes[1].x = self.width - 76
            self.in_macro_edit_shapes[1].y = self.height - 18

    def initialize_in_macro_label(self):
        self.in_macro_edit_shapes = []
        self.in_macro_edit_shapes.append(shapes.Rectangle(0, 100, 60, 14,  color=(255,255,255,250), batch = self.batch, group = self.camera_hud))
        self.in_macro_edit_shapes.append(pyglet.text.Label('in macro',\
                        font_name='Segoe UI',\
                        bold="bold",\
                        font_size=10,\
                        color=(0,0,0,250),\
                        x=0,\
                        y=100,\
                        batch=self.batch,
                        group = self.camera_hud))
        self.check_for_macro_edit(False)

    def on_draw(self):
        """Clear the screen and draw shapes"""
        #check macroedit mode
        self.clear()
        self.recalculate_in_macro_label()
        self.batch.draw()
        #self.fps.draw()

    def on_key_press(self, symbols, modifiers):
        if pyglet.window.key.MOD_SHIFT & modifiers and \
            symbols == pyglet.window.key.N:
            print('shift')

        if pyglet.window.key.MOD_CTRL & modifiers and \
            symbols == pyglet.window.key.G:
            print('ctrl')
            self.toggle_grid()

        if symbols == pyglet.window.key.ESCAPE:
            if self.in_macro_edit != None:
                self.check_for_macro_edit(False)

    def clearScheme(self):
        self.shapes = []

    def check_mouse_onshape(self, mousex, mousey):

        def mouseInRect(x1,y1,x2,y2, mousex,mousey, tolerance):
            tolerance*=self.magnifier

            if x1>x2:
                b = x1
                x1 = x2
                x2 = b
            if y1>y2:
                b = y1
                y1 = y2
                y2 = b

            x1-=tolerance
            x2+=tolerance
            y1-=tolerance
            y2+=tolerance

            if  mousex >= x1 and mousex <= x2 and\
                mousey >= y1 and mousey <= y2:
                    return True
            return False

        selected = []

        if self.scheme.jsonData and 'components' in self.scheme.jsonData:
            for component in self.scheme.jsonData['components']:
                if isinstance(component['temp_shapes'],SCHEME_DRAW_ITEM):
                    minx = 0
                    miny = 0
                    maxx = 0
                    maxy = 0
                    temp_shapes = component['temp_shapes']
                    for shape in temp_shapes.shapes:
                        if isinstance(shape, shapes.Line):
                            if mouseInRect(shape.x,shape.y,shape.x2,shape.y2,mousex,mousey,0.5):
                                #print('component',component['name'],'has shape under mouse: x,y',shape.x,shape.y,str(shape))
                                selected.append(component)
                                break
                        if isinstance(shape, shapes.Rectangle):
                            if mouseInRect(shape.x,shape.y,shape.x+shape.width,shape.y+shape.height,mousex,mousey,0.5):
                                #print('component',component['name'],'has shape under mouse: x,y',shape.x,shape.y,str(shape))
                                selected.append(component)
                                break
        return selected


    def loadShapesFromJson(self, targetComponent = None, onlyBounds = False, macro_mode = False):
        if self.scheme.jsonData != None:
            self.__schemeBatch = pyglet.graphics.Batch()

            def border_dot(x,y):
                return shapes.Star( x, y, outer_radius = self.border_dots_width,
                                    inner_radius = self.border_dots_width/3,
                                    num_spikes = 10,
                                    rotation = 120,
                                    color = self.borders_color,
                                    batch=self.batch,
                                    group=self.camera)

            def copare_bounds(x1,x2,y1,y2):
                #nonlocal maxx,minx,maxy,miny

                if x1 < self.minx: self.minx = x1
                if x2 < self.minx: self.minx = x2
                if x1 > self.maxx: self.maxx = x1
                if x2 > self.maxx: self.maxx = x2

                if y1 < self.miny: self.miny = y1
                if y2 < self.miny: self.miny = y2
                if y1 > self.maxy: self.maxy = y1
                if y2 > self.maxy: self.maxy = y2

            def loadShapesFromComponent(component, onlyBounds = False, macro_mode = False):
                x0 = component['x']
                y0 = component['y']

                boundminx, boundminy, boundmaxx, boundmaxy = (100000,100000,-100000,-100000)

                def compare_internal_bounds(x1,x2,y1,y2):
                    nonlocal boundmaxx, boundmaxy, boundminx, boundminy

                    if x1 < boundminx: boundminx = x1
                    if x2 < boundminx: boundminx = x2
                    if x1 > boundmaxx: boundmaxx = x1
                    if x2 > boundmaxx: boundmaxx = x2

                    if y1 < boundminy: boundminy = y1
                    if y2 < boundminy: boundminy = y2
                    if y1 > boundmaxy: boundmaxy = y1
                    if y2 > boundmaxy: boundmaxy = y2

                if onlyBounds == False:
                    component['temp_shapes'] = SCHEME_DRAW_ITEM()

                if 'shapes' in component:
                    for shape in component['shapes']:
                        if shape['type'] == "line":
                            x1 = shape['x1']+x0
                            x2 = shape['x2']+x0
                            y1 = shape['y1']+y0
                            y2 = shape['y2']+y0

                            x1*=self.magnifier
                            x2*=self.magnifier
                            y1*=self.magnifier
                            y2*=self.magnifier

                            copare_bounds(x1,x2,y1,y2)
                            compare_internal_bounds(x1,x2,y1,y2)

                            line = shapes.Line(         x1, y1,\
                                                        x2,y2,\
                                                        width=shape['width']*self.magnifier,\
                                                        color=(shape['color'][0], shape['color'][1], shape['color'][2],shape['color'][3]),\
                                                        batch=self.batch,\
                                                        group=self.camera)

                            if onlyBounds == False:
                                component['temp_shapes'].addItem(line)

                                if macro_mode:
                                    component['temp_shapes'].addItem(border_dot(x1, y1))
                                    component['temp_shapes'].addItem(border_dot(x2, y2))



                            #self.__shapes.append(line)

                        if shape['type'] == "rectangle":
                            x1 = shape['x1']+x0
                            x2 = shape['x2']+x0
                            y1 = shape['y1']+y0
                            y2 = shape['y2']+y0

                            x1*=self.magnifier
                            x2*=self.magnifier
                            y1*=self.magnifier
                            y2*=self.magnifier

                            copare_bounds(x1,x2,y1,y2)
                            compare_internal_bounds(x1,x2,y1,y2)

                            color=(shape['color'][0], shape['color'][1], shape['color'][2],shape['color'][3])

                            rect = shapes.Rectangle(x1,y1,x2-x1,y2-y1,color,\
                                                batch=self.batch,\
                                                group=self.camera)

                            if onlyBounds == False:
                                component['temp_shapes'].addItem(rect)

                                if macro_mode:
                                    component['temp_shapes'].addItem(border_dot(x1, y1))
                                    component['temp_shapes'].addItem(border_dot(x1, y2))
                                    component['temp_shapes'].addItem(border_dot(x2, y1))
                                    component['temp_shapes'].addItem(border_dot(x2, y2))

                if 'labels' in component:
                    for label in component['labels']:
                        x = label['x']+x0
                        y = label['y']+y0


                        x*=self.magnifier
                        y*=self.magnifier

                        copare_bounds(x1,x2,y1,y2)
                        compare_internal_bounds(x1,x2,y1,y2)

                        text = ''

                        if label['field'] == 'name':
                            text = component["name"]
                        else:
                            text = label['text']

                        if 'field_visible' in label and label['field_visible'] == True:
                            text = label['field'] + ":" + text


                        label = segoe_ui_semilbold = pyglet.text.Label(text,\
                            font_name=label['font']['name'],\
                            bold="semibold",\
                            font_size=label['font']['size']*self.magnifier,\
                            x=x,\
                            y=y,\
                            batch=self.batch,
                            group = self.camera)
                        #self.__shapes.append(line)

                        if onlyBounds == False:
                            component['temp_shapes'].addItem(label)
                if onlyBounds == True:
                    return (boundminx,boundminy,boundmaxx,boundmaxy)

            if targetComponent == None:
                if 'components' in self.scheme.jsonData:
                    for component in self.scheme.jsonData['components']:
                        loadShapesFromComponent(component)
            else:
                loadShapesFromComponent(targetComponent, onlyBounds = onlyBounds, macro_mode = macro_mode)



if __name__ == "__main__":
    cad = FEETCAD()
    cad.scheme.loadScheme('test.json')
    cad.loadShapesFromJson()
    cad.reset_view()
    cad.initialize_in_macro_label()
    cad.scheme.saveScheme('test_out.jschem')
    pyglet.app.run()
