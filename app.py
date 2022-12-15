#!/usr/bin/env python3

import sys
from typing import List

import tinydb
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from ui.mainwindow import Ui_MainWindow


class Todo:
    def __init__(self, content, finished=False):
        self.content: str = content
        self.finished = finished

    def finish(self):
        self.finished = True

    def unfinish(self):
        self.finished = False

    def json(self):
        return {
            "content": self.content,
            "finished": self.finished,
        }


class TodoItemModel(QtCore.QAbstractListModel):
    def __init__(self, parent, todos: List[Todo]):
        super().__init__(parent)
        self.todoData: List[Todo] = todos

    def flags(self, index):
        defaultFlags = super().flags(index)
        return (
            defaultFlags | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable
        )

    def data(self, index, role):
        todo = self.todoData[index.row()]
        if role == Qt.ItemDataRole.CheckStateRole:
            if todo.finished:
                return Qt.CheckState.Checked
            else:
                return Qt.CheckState.Unchecked
        elif role == Qt.ItemDataRole.DisplayRole:
            return todo.content
        elif role == Qt.ItemDataRole.BackgroundRole:
            if todo.finished:
                return QtGui.QColor("green")
        elif role == Qt.ItemDataRole.EditRole:
            return todo.content
        return None

    def setData(self, index, value, role):
        if index.isValid():
            todo = self.todoData[index.row()]
            if role == Qt.ItemDataRole.CheckStateRole:
                value = Qt.CheckState(value)
                if value == Qt.CheckState.Checked:
                    todo.finish()
                else:
                    todo.unfinish()
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            elif role == Qt.ItemDataRole.EditRole:
                todo.content = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
        return True

    def rowCount(self, _):
        return len(self.todoData)

    def addTodo(self, todo: Todo):
        self.beginInsertRows(
            QtCore.QModelIndex(), self.rowCount(None), self.rowCount(None) + 1
        )
        self.todoData.append(todo)
        self.endInsertRows()

    def removeTodo(self, index: QtCore.QModelIndex):
        self.beginRemoveRows(QtCore.QModelIndex(), index.row(), index.row() + 1)
        self.todoData.pop(index.row())
        self.endRemoveRows()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, todoModel: TodoItemModel):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.statusbar.showMessage("Todo List Ready...")
        self.todoModel = todoModel
        self.todoModel.setParent(self)
        self.todoList.setModel(self.todoModel)

    def addTodo(self):
        text = self.todoInput.text()
        todo = Todo(text)
        self.todoModel.addTodo(todo)
        self.todoInput.clear()
        self.statusbar.showMessage("Add new item.", 2000)

    def removeTodo(self):
        for index in self.todoList.selectedIndexes():
            self.todoModel.removeTodo(index)
            self.statusbar.showMessage("Remove item.", 2000)


if __name__ == "__main__":
    db = tinydb.TinyDB("db.json")
    initTodos = []
    for item in db:
        todo = Todo(item["content"], item["finished"])
        initTodos.append(todo)
    app = QtWidgets.QApplication(sys.argv)
    todoModel = TodoItemModel(None, initTodos)
    mainWindow = MainWindow(todoModel)
    mainWindow.show()
    app.exec()
    db.drop_tables()
    for todo in todoModel.todoData:
        db.insert(todo.json())
