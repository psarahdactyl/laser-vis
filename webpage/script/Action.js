class Action {
  constructor(line) {
    this.line = line;
    this.draw = false;
    this.modify = false;
    this.delete = false;
  }

  assignAction(actionNumber) {
    if(actionNumber == 0)
      this.draw = true;
    else if(actionNumber == 1)
      this.modify = true;
    else if(actionNumber == 2)
      this.delete = true;
  }


}