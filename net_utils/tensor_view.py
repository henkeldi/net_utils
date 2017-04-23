# -*- coding: utf-8 -*-
import os
import numpy as np

from OpenGL.GL import *

import gl_utils as gu

class TensorView(object):

    def __init__(self, W, H, vmin=-1, vmax=1):
        self.__window = gu.Window(W, H, 2, 'TensorView', monitor=None, show_at_center=False)

        gu.Shader.shaderFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shader')
        shader = gu.Shader('shader.vs', 'shader.frag')
        shader.compile_and_use()
        glUniform1f(3, 1.0/(float(vmax) - float(vmin)))
        glUniform1f(4, float(vmin))

        self.camera = gu.Camera()
        controller = gu.controller.Controller2D(self.camera, self.__window, scale=10, zoom_limits=[0.0001, 100], borders=[-100000, 100000, -100000, 100000])

        self.scene_buffer = gu.ShaderStorage(0, self.camera.data, True)
        self.scene_buffer.bind()

        colormap_data = gu.colormap.coolwarm
        colormap_tex = gu.Texture1D(1, GL_RGB8, colormap_data.shape[0])
        colormap_tex.setFilter(GL_NEAREST, GL_NEAREST)
        colormap_tex.setWrap(GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE)
        colormap_tex.subImage(0, 0, colormap_data.shape[0], GL_RGB, GL_UNSIGNED_BYTE, np.flipud(colormap_data).copy())
        colormap_tex.makeResident()
        self.colormap_buffer = gu.ShaderStorage(2, np.array([colormap_tex.handle], dtype=np.uint64))
        self.colormap_buffer.bind()

        glClearColor(0.05, 0.05, 0.05, 1.0)
        self.first_update = True
        self.tensors = None

    def update(self, tensors, use_colormap=None):
        if self.first_update:
            if use_colormap==None:
               use_colormap = len(tensors)*[True] 
            self.use_colormap = use_colormap
            self.__init_textures__(tensors)
            self.__init_vao__(tensors)
            self.first_update = False
        for texture, tensor in zip(self.textures, tensors):
            IMG_H, IMG_W, IMG_C = tensor.shape[1:4]
            texture.subImage(0, 0, 0, 0, IMG_W, IMG_H, IMG_C, GL_RED, GL_FLOAT, tensor[0])
        self.tensors = tensors

    def __init_textures__(self, tensors):
        self.textures = []
        for tensor in tensors:
            IMG_H, IMG_W, IMG_C = tensor.shape[1:4]
            texture = gu.Texture3D(GL_TEXTURE_2D_ARRAY, 1, GL_R32F, IMG_W, IMG_H, IMG_C)
            texture.subImage(0, 0, 0, 0, IMG_W, IMG_H, IMG_C, GL_RED, GL_FLOAT, tensor[0])
            texture.setFilter(GL_NEAREST, GL_NEAREST)
            texture.setWrap(GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE)
            texture.makeResident()
            self.textures.append(texture)
    
        handles = [tex.handle for tex in self.textures]
        self.tex_buffer = gu.ShaderStorage(1, np.array(handles, dtype=np.uint64) , True)
        self.tex_buffer.bind()

    def __init_vao__(self, tensors):
        vertex_data = []
        for tensor in tensors:
            IMG_H, IMG_W = tensor.shape[1:3]
            pos, uv = gu.geo.quad(True)
            pos[:,0] *= IMG_W / 2.0
            pos[:,1] *= IMG_H / 2.0
            pos *= 100.0
            vertex_data.append(np.hstack( (pos, uv) ).reshape(-1))

        cube_vao = gu.VAO({ (gu.Vertexbuffer( np.array(vertex_data) ), 0, 5*4):
                        [(0, 3, GL_FLOAT, GL_FALSE, 0),
                         (1, 2, GL_FLOAT, GL_FALSE, 3*4)]})
        cube_vao.bind()

    def is_open(self):
        return self.__window.is_open()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.__window.framebuf_width, self.__window.framebuf_height)

        self.scene_buffer.update(self.camera.data)
        
        if isinstance(self.tensors, list):                
            TENSOR_H, TENSOR_W, TENSOR_C = self.tensors[0].shape[1:4]
            aspect = float(TENSOR_H) / float(TENSOR_W)
            offset_x = - 0.5 * TENSOR_W * 100
            padding_x = 50
            padding_y = 50
            for i, tensor in enumerate(self.tensors):
                glUniform1i(1, self.use_colormap[i])
                TENSOR_H, TENSOR_W, TENSOR_C = tensor.shape[1:4]
                aspect = float(TENSOR_H) / float(TENSOR_W)
                offset_y = -0.5*float(TENSOR_H*100.0*TENSOR_C + (TENSOR_C-1.0)*padding_y)
                for d in xrange(tensor.shape[3]):
                    glUniform1i(2, i)
                    model = np.eye(4)
                    model[0,3] = offset_x + TENSOR_W * 0.5* 100.0
                    model[1,3] = offset_y + TENSOR_H * 0.5 * 100.0
                    offset_y += TENSOR_H * 100.0 + padding_y
                    glUniformMatrix4fv(0, 1, True, model)
                    glUniform1f(5, float(d)) # tex_layer
                    glDrawArrays(GL_TRIANGLE_STRIP, i*4, 4)   
                offset_x += TENSOR_W* 100 + padding_x

        self.__window.update()
