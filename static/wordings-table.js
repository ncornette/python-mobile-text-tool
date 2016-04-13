
  var languages = [];
  var wordings = [];

  var grid;
  var data = [];
  var columns = [];
  var options = {};


  function setWordings(new_languages, new_wordings) {
    languages = new_languages;
    wordings = new_wordings;

    columns = [
      {id: "key", name: "Key", field: "key", width: 120, cssClass: "cell-key", editor: Slick.Editors.Text, validator: requiredFieldValidator},
      {id: "exportable", name: "Exportable", width: 40, minWidth: 10, maxWidth: 80, cssClass: "cell-exportable", field: "exportable", formatter: Slick.Formatters.Checkmark, editor: Slick.Editors.Checkbox},
      {id: "is_comment", name: "Is Comment", width: 40, minWidth: 10, maxWidth: 80, cssClass: "cell-is-comment", field: "is_comment", formatter: Slick.Formatters.Checkmark, editor: Slick.Editors.Checkbox},
      {id: "comment", name: "Comment", field: "comment", width: 100, editor: Slick.Editors.LongText},

      //{id: "%", name: "% Complete", field: "percentComplete", width: 80, resizable: false, formatter: Slick.Formatters.PercentCompleteBar, editor: Slick.Editors.PercentComplete},
      //{id: wordings_fields[0], name: "Duration", field: "duration", editor: Slick.Editors.Text},
      //{id: "start", name: "Start", field: "start", minWidth: 60, editor: Slick.Editors.Date},
      //{id: "finish", name: "Finish", field: "finish", minWidth: 60, editor: Slick.Editors.Date},
      //{id: "effort-driven", name: "Effort Driven", width: 80, minWidth: 20, maxWidth: 80, cssClass: "cell-effort-driven", field: "effortDriven", formatter: Slick.Formatters.Checkmark, editor: Slick.Editors.Checkbox}
    ];

    for (var  i = 0; i < languages.length; i++) {
      l = languages[i]
      columns.push({id: l, name: l, field: l, width: 100, editor: Slick.Editors.LongText})
    }

    options = {
      editable: true,
      enableAddRow: true,
      enableCellNavigation: true,
      asyncEditorLoading: false,
      autoEdit: false
    };

  }

  function requiredFieldValidator(value) {
    if (value == null || value == undefined || !value.length) {
      return {valid: false, msg: "This is a required field"};
    } else {
      return {valid: true, msg: null};
    }
  }

  $(function () {
    for (var i = 0; i < wordings.length; i++) {
      var d = (data[i] = {});
      var w = wordings[i]

      d["key"] = w.key;
      d["exportable"] = w.exportable;
      d["is_comment"] = w.is_comment;
      d["comment"] = w.comment;

      for (var  j = 0; j < languages.length; j++) {
          l = languages[j]
          d[l] = w.translations[l];
      }
    }

    grid = new Slick.Grid("#myGrid", data, columns, options);

    grid.setSelectionModel(new Slick.CellSelectionModel());

    grid.onAddNewRow.subscribe(function (e, args) {
      var item = args.item;
      grid.invalidateRow(data.length);
      data.push(item);
      grid.updateRowCount();
      grid.render();
    });
  })
