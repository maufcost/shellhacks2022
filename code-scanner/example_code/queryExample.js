app.post("/records", (request, response) => {
  const data = request.body;
  const query = `SELECT * FROM health_records WHERE id = (${data.id})`;
  connection.query(request.get['userInput'], (err, rows) => {
    if(err) throw err;
    response.json({data:rows});
  });
});
