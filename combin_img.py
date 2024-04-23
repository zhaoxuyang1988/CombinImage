# coding:utf-8
import ctypes
import time

import wx
from PIL import Image

ctypes.windll.shcore.SetProcessDpiAwareness(True)

DIRECTION_H = 1
DIRECTION_W = 0


def pil_to_wxbitmap(pil_image):
    width, height = pil_image.size
    pil_image = pil_image.convert("RGB")  # 转换为RGB模式
    wx_image = wx.Image(width, height)
    wx_image.SetData(pil_image.tobytes())
    wx_bitmap = wx.Bitmap(wx_image)
    return wx_bitmap


def scale_bitmap(bitmap, width, height):
    image = wx.Bitmap.ConvertToImage(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.Bitmap(image)
    return result


def load_bitmap(f_image, width=None, height=None):
    bmp = wx.Bitmap(f_image)
    ori_width, ori_height = bmp.Size
    # height or width is None use original size
    width = width or ori_width
    height = height or ori_height
    if width == ori_width and height == ori_height:
        return bmp
    return scale_bitmap(bmp, width, height)


class ImgPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent, size=(600, 400))
        self.sizer = wx.BoxSizer(wx.VERTICAL)

    def set_img(self, img):
        # self.clear()
        if hasattr(self, 'static_bitmap'):
            self.static_bitmap.SetBitmap(img)
        else:
            self.static_bitmap = wx.StaticBitmap(self, wx.BITMAP_TYPE_ANY, img)
            self.sizer.Add(self.static_bitmap, 1, wx.EXPAND | wx.ALL, 5)
            self.SetSizer(self.sizer)

        # del self.static_bitmap
        # self.static_bitmap = static_bitmap

    def clear(self):
        if hasattr(self, 'static_bitmap'):
            self.static_bitmap.SetBitmap(wx.Bitmap(1, 1))
        self.Refresh()


class ImageFrame(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent=parent, title=title, size=(800, 600))

        self.img_panel = ImgPanel(self)
        # self.img_panel.Disable()
        self.img1 = None
        self.img2 = None
        self.mix_img = None
        self.btn_import_img1 = wx.Button(self, wx.ID_ANY, "...", size=(50, -1))
        self.btn_import_img2 = wx.Button(self, wx.ID_ANY, "...", size=(50, -1))
        self.tx_img1 = wx.TextCtrl(self, wx.ID_ANY, "", )
        self.tx_img1.Enable(False)
        self.tx_img2 = wx.TextCtrl(self, wx.ID_ANY, "", )
        self.tx_img2.Enable(False)

        img1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        img1_sizer.Add((10, -1))
        img1_sizer.Add(wx.StaticText(self, wx.ID_ANY, "图像1:", size=(70, -1)), 0, wx.ALIGN_CENTER | wx.ALL)
        img1_sizer.Add((5, -1))
        img1_sizer.Add(self.tx_img1, 1, wx.EXPAND | wx.ALL)
        img1_sizer.Add(self.btn_import_img1, 0, wx.ALIGN_CENTER | wx.ALL)
        img1_sizer.Add((10, -1))

        img2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        img2_sizer.Add((10, -1))
        img2_sizer.Add(wx.StaticText(self, wx.ID_ANY, "图像2:", size=(70, -1)), 0, wx.ALIGN_CENTER | wx.ALL)
        img2_sizer.Add((5, -1))
        img2_sizer.Add(self.tx_img2, 1, wx.EXPAND | wx.ALL)
        img2_sizer.Add(self.btn_import_img2, 0, wx.ALIGN_CENTER | wx.ALL)
        img2_sizer.Add((10, -1))

        self.rd_h = wx.RadioButton(self, wx.ID_ANY, "水平")
        self.rd_h.SetValue(True)
        self.rd_v = wx.RadioButton(self, wx.ID_ANY, "垂直")

        self.cb_ex = wx.CheckBox(self, wx.ID_ANY, "扩展")
        self.cb_ex.SetValue(True)  # default True

        btn_clear = wx.Button(self, wx.ID_ANY, "清空", size=(100, -1))
        btn_save = wx.Button(self, wx.ID_ANY, "保存", size=(100, -1))

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add((10, -1), 1)
        btn_sizer.Add(self.rd_h, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        btn_sizer.Add(self.rd_v, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        btn_sizer.Add((30, -1))
        btn_sizer.Add(self.cb_ex, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        btn_sizer.Add(btn_clear, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        btn_sizer.Add(btn_save, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        btn_sizer.Add((10, -1))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add((-1, 10))
        self.sizer.Add(img1_sizer, 0, wx.EXPAND | wx.ALL)
        self.sizer.Add((-1, 5))
        self.sizer.Add(img2_sizer, 0, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.img_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.sizer)


        self.btn_import_img1.Bind(wx.EVT_BUTTON, self.OnImport)
        self.btn_import_img2.Bind(wx.EVT_BUTTON, self.OnImport)

        self.rd_h.Bind(wx.EVT_RADIOBUTTON, self.OnChangeParam)
        self.rd_v.Bind(wx.EVT_RADIOBUTTON, self.OnChangeParam)
        self.cb_ex.Bind(wx.EVT_CHECKBOX, self.OnChangeParam)

        btn_clear.Bind(wx.EVT_BUTTON, self.OnClear)
        btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):

        self.Destroy()

    def OnChangeParam(self, event):
        event.Skip()
        self.mix()

    def mix(self):
        wx.BeginBusyCursor()
        if self.img1 and self.img2:
            direction = DIRECTION_H if self.rd_h.GetValue() else DIRECTION_W
            ex = self.cb_ex.GetValue()
            mix_img = self.mix_image(self.img1, self.img2, direction, ex)
            self.mix_img = mix_img
            w, h = self.img_panel.GetClientSize()
            self.img_panel.set_img(scale_bitmap(pil_to_wxbitmap(mix_img), w, h))
        wx.EndBusyCursor()

    def mix_image(self, img1, img2, direction, ex_flg=True):
        # direction 0 -- w  1---h
        width, high = img1.size

        if ex_flg:
            new_size = (width * 2, high) if direction == DIRECTION_H else (width, high * 2)
            merged_image = Image.new('RGB', new_size)
            for x in range(width):
                for y in range(high):
                    pixel1 = img1.getpixel((x, y))
                    pixel2 = img2.getpixel((x, y))
                    if direction == DIRECTION_W:
                        merged_image.putpixel((x, y * 2), pixel1)
                        merged_image.putpixel((x, y * 2 + 1), pixel2)
                    else:
                        merged_image.putpixel((x * 2, y), pixel1)
                        merged_image.putpixel((x * 2 + 1, y), pixel2)
        else:
            merged_image = Image.new('RGB', img1.size)

            for x in range(width):
                for y in range(high):
                    pixel1 = img1.getpixel((x, y))
                    pixel2 = img2.getpixel((x, y))
                    if direction == DIRECTION_W:
                        if x % 2 == 0:
                            merged_image.putpixel((x, y), pixel1)
                        else:
                            merged_image.putpixel((x, y), pixel2)
                    else:
                        if y % 2 == 0:
                            merged_image.putpixel((x, y), pixel1)
                        else:
                            merged_image.putpixel((x, y), pixel2)

        return merged_image

    def OnImport(self, event):
        event.Skip()
        wildcard = "Image files (*.jpg)|*.jpg|(*.jpeg)|*.jpeg|(*.png)|*.png|(*.bmp)|*.bmp|All files (*.*)|*.*"
        dialog = wx.FileDialog(self, message="Choose a image", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            return

        path = dialog.GetPath()
        dialog.Destroy()
        try:
            img = Image.open(path)
        except Exception as error:
            wx.MessageBox(f"load image with {error}")
            return
        if event.EventObject == self.btn_import_img1:
            if self.img2 is not None and self.img2.size != img.size:
                wx.MessageBox(f"Image Size not Same!\nImage2:{self.img2.size} Image1:{img.size}")
                return
        else:
            if self.img1 is not None and self.img1.size != img.size:
                wx.MessageBox(f"Image Size not Same!\nImage1:{self.img1.size} Image1:{img.size}")
                return

        if event.EventObject == self.btn_import_img1:
            self.tx_img1.SetValue(path)
            self.img1 = img
        else:
            self.tx_img2.SetValue(path)
            self.img2 = img

        if self.img1 and self.img2:
            self.mix()
        else:
            w, h = self.img_panel.GetClientSize()
            self.img_panel.set_img(scale_bitmap(pil_to_wxbitmap(img), w, h))

    def OnClear(self, event):
        self.img1 = None
        self.img2 = None
        self.mix_img = None
        self.img_panel.clear()
        self.tx_img1.SetValue("")
        self.tx_img2.SetValue("")
        event.Skip()

    def OnSave(self, event):
        # todo save
        event.Skip()
        if not self.mix_img:
            wx.MessageBox("没有结果图片")
            return
        wildcard = "Image files (*.png)|*.png|(*.jpg)|*.jpg"
        dialog = wx.FileDialog(self, message="Save file as", defaultFile="output.png",
                               wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            return
        filepath = dialog.GetPath()

        try:
            self.mix_img.save(filepath)
            wx.MessageBox("保存成功")
        except Exception as error:
            wx.MessageBox(f"保存失败 {error}")


if __name__ == '__main__':
    app = wx.App()
    frame = ImageFrame(None, "Image Viewer")
    frame.Show()
    app.MainLoop()
