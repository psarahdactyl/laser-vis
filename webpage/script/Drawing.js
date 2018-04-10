class Drawing {
  constructor(lines) {
    this.lines = lines;
    this.count = 0;
    this.selected = [];
    this.history = [];
  }

  addToDrawing(line) {
    this.lines.push(line);
    var action = new Action(line);
    action.assignAction(0); // is a drawing action
    this.addToHistory(action);
  }

  deleteFromDrawing(line) {
    var index = this.lines.indexOf(line);
    this.lines.splice(index, 1);
    var action = new Action(line);
    action.assignAction(2); // is a deletion action
    this.addToHistory(action);
  }

  modifyDrawing(line) {
    var action = new Action(line);
    action.assignAction(1); // is a modify action
    this.addToHistory(action);
  }

  addToSelection(line) {
    this.selected.push(line);
  }

  deleteFromSelection(line) {
    this.selected.pop();
  }

  addToHistory(action) {
    this.history.push(action);
  }

  deleteFromHistory(action) {
    lastState = this.history.pop();
    //TODO: undo last action
  }

  isSelected() {
    if(this.selected.length == 0)
      return true;
    return false;
  }

  isEmpty() {
    if(this.lines.length == 0)
      return true;
    return false;
  }

  emptiness() {
    return this.isEmpty();
  }

  getLastAction() {
    return this.history[-1];
  }


}
 

Object.defineProperties(Drawing.prototype, {
  count : {
    get : function() {
      return this._count;
    },
    set : function(value) {
      this._count = value;
    }
  }
 });




