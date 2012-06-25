#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wxReversePolishNotation
参照: 放送大学講座 2008 年 コンピュータのしくみ 岡部洋一
逆ポーランド記法電卓 状態遷移図
0 除算ノーチェック

・phase = 0
  ・キーボードチェックを繰り返す
    ・数字キー, phase == 0   / phase = 1, Rz = Ry, Ry = Rx (push), Rx = 数字
    ・数字キー, phase == 1 d / Rx = Rx * 10 +(-) 数字
    ・数字キー, phase == 1 h / Rx = Rx * 16 +(-) 数字
    ・Enterキー              / phase = 0 ※push バグ修正 数字キー phase 0 へ
    ・演算キー               / phase = 0, Rx = Rx @ Ry, Ry = Rz (pop)
    ・(-) キー               / phase = 0, Rx = - Rx
    ・AC キー                / phase = 0, Rx = 0, Ry = 0, Rz = 0, ...
    ・C キー                 / phase = 0, Rx = 0
  ・繰り返し

 C D E F hd
 B 7 8 9 /
 A 4 5 6 x
ac 1 2 3 -
 c 0 . e +
'''

import wx

class ReversePolishNotation(object):
  def __init__(self, n):
    self.phase, self.digit, self.regs = 0, 10, ([0] * n)

  def push(self): # [1] が stack の先頭 ([0] は変化しない)
    for i in xrange(len(self.regs) - 1, 0, -1): self.regs[i] = self.regs[i - 1]

  def pop(self):
    r = self.regs[1] # [1] が stack の先頭 ([0] は変化しない)
    for i in xrange(1, len(self.regs) - 1): self.regs[i] = self.regs[i + 1]
    return r

  def fetch(self, k):
    if ord('0') <= ord(k) <= ord('9') or ord('A') <= ord(k) <= ord('F'):
      n = ord(k) - (ord('0') if ord(k) < ord('A') else (ord('A') - 10))
      if self.phase == 0:
        self.phase = 1
        self.push()
        self.regs[0] = n
      else:
        self.regs[0] = self.regs[0] * self.digit + n
    else:
      if k == 'h': self.digit = 16 if self.digit == 10 else 10
      elif k == 'e': self.phase = 0
      elif k == 'a':
        self.phase = 0
        for i in xrange(len(self.regs)): self.regs[i] = 0
      elif k == 'c':
        self.phase = 0
        self.regs[0] = 0
      elif k == '-':
        self.phase = 0
        self.regs[0] = -self.regs[0]
      elif k == '+':
        self.phase = 0
        self.regs[0] += self.pop()
      elif k == '/':
        self.phase = 0
        self.regs[0] = self.pop() / self.regs[0] # 0 除算ノーチェック
      elif k == 'x':
        self.phase = 0
        self.regs[0] *= self.pop()
      else: wx.Bell() # .

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    super(MyFrame, self).__init__(title=u'wxReversePolishNotation',
      style=wx.DEFAULT_FRAME_STYLE,
      pos=(320, 240), size=(640, 240), *args, **kwargs)
    self.rpn = ReversePolishNotation(16)
    self.kbr = {}
    hsz = wx.BoxSizer(wx.HORIZONTAL)
    if True:
      self.pnl = wx.Panel(self, -1)
      vsz = wx.BoxSizer(wx.VERTICAL)
      if True:
        self.txt = wx.TextCtrl(self.pnl, id=wx.NewId())
        vsz.Add(self.txt, 0, wx.EXPAND)
        self.sum = wx.TextCtrl(self.pnl, id=wx.NewId(), value='0')
        vsz.Add(self.sum, 0, wx.EXPAND)
        self.mode = wx.StaticText(self.pnl, -1, u'')
        vsz.Add(self.mode, 0, wx.EXPAND)
        self.stack = wx.ListCtrl(self.pnl, -1, style=wx.LC_REPORT|wx.LC_HRULES)
        RIGHT = wx.LIST_FORMAT_RIGHT
        self.stack.InsertColumn(0, u'stack', format=RIGHT, width=60)
        self.stack.InsertColumn(1, u'value', format=RIGHT, width=-1)
        vsz.Add(self.stack, 1, wx.EXPAND)
      self.pnl.SetSizer(vsz)
      hsz.Add(self.pnl, 2, wx.EXPAND)
    if True:
      self.kbd = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
      gsz = wx.GridSizer(5, 5, 3, 5)
      keyboard = 'CDEFhB789/A456xa123-c0.e+' # 5 x 5
      for r in xrange(5):
        for c in xrange(5):
          k = keyboard[r * 5 + c]
          if k == 'h': txt = 'hex <-> dec'
          elif k == 'a': txt = 'all clear'
          elif k == 'c': txt = 'clear'
          elif k == 'e': txt = 'enter'
          else: txt = k
          id = wx.NewId()
          self.kbr[id] = k
          btn = wx.Button(self.kbd, id, txt, size=(80, 30))
          self.Bind(wx.EVT_BUTTON, self.OnButton, btn)
          gsz.Add(btn, 1, wx.EXPAND) # r, c
      self.kbd.SetSizer(gsz)
      hsz.Add(self.kbd, 5, wx.EXPAND)
    self.SetSizer(hsz)
    self.RefreshBtn()
    self.RefreshStack()

  def OnButton(self, ev):
    k = self.kbr[ev.GetId()]
    self.txt.SetValue(k)
    self.rpn.fetch(k)
    if k == 'h': self.RefreshBtn() # must be called after fetch
    self.RefreshStack()

  def RefreshBtn(self):
    self.mode.SetLabel(
      u'mode: %s' % (u'decimal' if self.rpn.digit == 10 else u'hex'))
    for id in self.kbr.keys():
      if self.kbr[id] in 'ABCDEF':
        self.kbd.FindWindowById(id).Enable(self.rpn.digit != 10)

  def RefreshStack(self):
    self.stack.DeleteAllItems()
    for i in xrange(len(self.rpn.regs)):
      self.stack.InsertStringItem(i, hex(i))
      self.stack.SetStringItem(i, 1, hex(self.rpn.regs[i]))

if __name__ == '__main__':
  app = wx.App(False)
  frm = MyFrame(parent=None, id=-1)
  app.SetTopWindow(frm)
  frm.Show()
  app.MainLoop()
