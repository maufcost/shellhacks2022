var fs = require('fs')
var csv = require("csvtojson")
const express = require('express')

const filePath = "../Securities - Schonfeld ShellHacks.csv"

// Setting up express server
const app = express()
const port = 3000

// Convert CSV to JSON
let json = []
csv()
.fromFile(filePath)
.then(jsonArr => {
    console.log("Done reading csv")

    json = jsonArr

    // Writing to file locally.
    fs.writeFile('securities.json', JSON.stringify(jsonArr), 'utf8', () => {
        console.log("Done exporting json")
    })
})

// Routes
app.get('/', (req, res) => {
    res.send(json)
})

app.listen(port, () => {
    console.log(`Preprocessor API listening on port ${port}`)
})