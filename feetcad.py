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

        with open(self.__fileName, 'w') as f:
            f.write(json.dumps(self.jsonData, indent=4))

class FEETCAD(pyglet.window.Window):

    def __init__(self):
        config = pyglet.gl.Config()
        config.sample_buffers = 1
        config.samples = 4
        super(FEETCAD,self).__init__(720, 480, "FEETCAD",config=config,resizable=True,style=pyglet.window.Window.WINDOW_STYLE_DEFAULT)
        self.time = 0
        self.__grid_batch = pyglet.graphics.Batch()
        self.circle = shapes.Circle(360, 240, 75, color=(255, 225, 255, 250))
        self.scheme = SCHEME()
        self.batch = pyglet.graphics.Batch()
        self.camera = CenteredCameraGroup(self,0,0,1)
        self.__clickTime = time.time()
        self.__shapes = []

        self.__grid_shapes_big = []
        self.__grid_shapes_small = []
        self.__grid_camera = CameraGroup(self,0,0,1)

        self.__shapes_hud = []
        self.__grid_visible = False
        self.__last_grid_state = True
        self.grid_width = 2
        self.grid_step = 1
        self.grid_steps = 40
        self.grid_min_cell_width = 20
        self.grid_zoom_step = 10
        self.grid_zero_color = color=(255,255,255,150)
        self.grid_primary_color = color=(255,255,255,100)
        self.grid_middle_color = color=(255,255,255,50)
        self.grid_secondary_color = color=(255,255,255,25)

        self.zoom_step = 5


        self.generate_grid()


    def initialize_hud(self):
        __shapes_hud = []
        line = shapes.Line(         0, 0,\
                                    100,100,\
                                    5,\
                                    color=(255, 255,255,255),\
                                    batch=self.batch,\
                                    group=self.camera_hud)
        self.__shapes_hud.append(line)

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

        cell_width = self.grid_step*self.camera.zoom
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
        middley = (self.grid_steps*self.grid_step*zoom_factor)/2


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
            x+=1

            if not self.__grid_visible:
                line.x+=1000000

        y = 0
        for line in self.__grid_shapes_big[0]:
            line.y = y*self.grid_step*zoom_factor-middley+self.camera.y-self.camera.y%(zoom_factor*self.grid_step)

            if line.x  == 0:
                line.color = self.grid_zero_color
            elif line.y % (self.grid_zoom_step*zoom_factor) == 0:
                line.color = self.grid_primary_color
            elif line.y % (self.grid_zoom_step/2*zoom_factor) == 0:
                line.color = self.grid_middle_color
            else:
                line.color = self.grid_secondary_color

            line.height = self.grid_width/self.camera.zoom
            line.y-=line.height/2
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
        scheme_width = self.maxx - self.minx+20
        scheme_height = self.maxy - self.miny+20
        max_dim_scheme, max_dim_window = (0, 0)

        if scheme_width > scheme_height:
            max_dim_scheme = scheme_width
            max_dim_window = self.width
        else:
            max_dim_scheme = scheme_height
            max_dim_window = self.height

        zoom = max_dim_window/max_dim_scheme
        self.camera.zoom=zoom
        self.camera.x = self.minx+(self.maxx-self.minx)/2
        self.camera.y = self.miny+(self.maxy-self.miny)/2
        self.recalculate_grid()


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


    def on_draw(self):
        """Clear the screen and draw shapes"""
        self.clear()
        self.batch.draw()

    def update(self, delta_time):
        """Animate the shapes"""
        self.time += delta_time
        self.circle.radius = 75 + math.sin(self.time * 1.17) * 25

    def on_key_press(self, symbols, modifiers):
        if pyglet.window.key.MOD_SHIFT & modifiers and \
            symbols == pyglet.window.key.N:
            print('shift')

        if pyglet.window.key.MOD_CTRL & modifiers and \
            symbols == pyglet.window.key.G:
            print('ctrl')
            self.toggle_grid()

    def clearScheme(self):
        self.shapes = []


    def loadShapesFromJson(self):
        if self.scheme.jsonData != None:
            self.__schemeBatch = pyglet.graphics.Batch()
            self.miny,self.minx,self.maxy,self.maxx = (100,100,-100,-100)

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

            if 'components' in self.scheme.jsonData:
                for component in self.scheme.jsonData['components']:
                    x = component['x']
                    y = component['y']
                    if 'shapes' in component:
                        for shape in component['shapes']:
                            if shape['type'] == "line":
                                x1 = shape['x1']+x
                                x2 = shape['x2']+x
                                y1 = shape['y1']+y
                                y2 = shape['y2']+y
                                copare_bounds(x1,x2,y1,y2)

                                line = shapes.Line(         x1, y1,\
                                                            x2,y2,\
                                                            width=shape['width'],\
                                                            color=(shape['color'][0], shape['color'][1], shape['color'][2],shape['color'][3]),\
                                                            batch=self.batch,\
                                                            group=self.camera)
                                self.__shapes.append(line)

                            if shape['type'] == "rectangle":
                                x1 = shape['x1']+x
                                x2 = shape['x2']+x
                                y1 = shape['y1']+y
                                y2 = shape['y2']+y
                                copare_bounds(x1,x2,y1,y2)

                                color=(shape['color'][0], shape['color'][1], shape['color'][2],shape['color'][3])

                                line = shapes.Line( x1,y1,x2,y1,\
                                                    width=shape['width'],\
                                                    color=color,\
                                                    batch=self.batch,\
                                                    group=self.camera)
                                self.__shapes.append(line)

                                line = shapes.Line( x2,y1,x2,y2,\
                                                    width=shape['width'],\
                                                    color=color,\
                                                    batch=self.batch,\
                                                    group=self.camera)
                                self.__shapes.append(line)

                                line = shapes.Line( x1,y1,x1,y2,\
                                                    width=shape['width'],\
                                                    color=color,\
                                                    batch=self.batch,\
                                                    group=self.camera)
                                self.__shapes.append(line)

                                line = shapes.Line( x1,y2,x2,y2,\
                                                    width=shape['width'],\
                                                    color=color,\
                                                    batch=self.batch,\
                                                    group=self.camera)
                                self.__shapes.append(line)
                print( 'minx,maxx,miny,maxy:', self.minx, self.maxx, self.miny, self.maxy)

if __name__ == "__main__":
    cad = FEETCAD()
    cad.scheme = SCHEME()
    cad.clearScheme()
    cad.scheme.loadScheme('test.jschem')
    cad.loadShapesFromJson()
    cad.reset_view()
    #cad.initialize_hud()
    cad.toggle_grid()
    #cad.scheme.saveScheme('test.jschem')
    pyglet.app.run()
