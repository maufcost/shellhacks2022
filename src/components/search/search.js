import React, { useState } from "react"

import './search.css'
import './search-area.css'

import SearchResult from '../search-result/search-result'

import { ROW_SCHEMA } from '../../row-schema'

const Search = () => {
    const [file, setFile] = useState(null)
    const [query, setQuery] = useState("")
    const [csvArray, setCSVArray] = useState([])
    const [securities, setSecurities] = useState([])
    const [searchResults, setSearchResults] = useState([])

    const fileReader = new FileReader();

    const handleFileChange = e => {
        if (!e) return
        setFile(e.target.files[0])
    };

    const handleFileImport = e => {
        e.preventDefault()

        if (file) {
            fileReader.onload = event => {
                const csvOutput = event.target.result;
                console.log(csvOutput)
                convertCSVFileToArray(csvOutput)
                fetchAvailableSecurities(csvOutput)
            };

            // Reads CSV as a regular string.
            fileReader.readAsText(file)
        }
    };

    const convertCSVFileToArray = csvString => {
        // We first get all the header labels
        const csvHeader = csvString.slice(0, csvString.indexOf("\n")).split(",")

        // Then, we are going to get all the rows as a string and put them in an array.
        // So, csvRows is now an array of strings where each string is a row.
        const csvRows = csvString.slice(csvString.indexOf("\n") + 1).split("\n")

        const csvArray = csvRows.map(r => {
            const values = r.split(",")
            
            // Returns a single object
            const obj = csvHeader.reduce((object, header, index) => {
                object[header] = values[index].replace(" ", "")
                return object
            }, {});

            return obj
        });

        console.log(csvArray)
        setCSVArray(csvArray)
    }

    const handleQueryChange = e => {
        setQuery(e.target.value)
    }

    const handleSearch = () => {
        // E.g. of a query: 00BV
        // OBS: Disconsider the security_id field

        // A way to improve this search even more
        // would be to let all the rows to continue
        // to be a string. This way, we don't have
        // to use loop - just a '.includes' on the row string.
        const results = []

        // Looping over the rows to look for a match or partial match
        for (let i = 0; i < csvArray.length; i++) {

            // Checking the properties of each security
            const keys = Object.keys(csvArray[i])
            keys.splice("security_id", 1)

            for (let j = 0; j < keys.length; j++) {

                console.log(csvArray[i][keys[j]])

                const cellValue = csvArray[i][keys[j]]

                if (cellValue.includes(query)) {
                    // Found a match or partial match
                    // Priority 1: full match
                    // Priority 2: partial match
                    let priority = 2

                    // Checking if it's a full match
                    // or partial match to adjust the way
                    // the result list will be shown
                    if (
                        (cellValue.indexOf(query) === 0) &&
                        (query.trim().length === cellValue.trim().length)
                    ) {
                        // Then, this is a full match
                        priority = 1
                    }else {
                        // Then, this is a partial match
                        // No more actions required.
                    }

                    results.push({
                        content: csvArray[i],
                        // These properties are useful for
                        // our match highlight feature
                        KeyWhereMatchWasFound: keys[j],
                        rowIndex: i,
                        priority
                    })
                }
            }
        }
        
        // Processing search priorities (ordering
        // the search results according to their priority in ascending order)
        console.log(results)
        results.sort((r1, r2) => r1.priority - r2.priority)

        setSearchResults(results)
    }

    const fetchAvailableSecurities = csvString => {
        const csvRows = csvString.slice(csvString.indexOf("\n") + 1).split("\n")
        const allSecurities = []

        csvRows.map(r => {
            const security = r.slice(0, r.indexOf(","))
            allSecurities.push(security)
        })

        setSecurities([...new Set(allSecurities)])
    }

    const renderSecuritiesDropdown = () => {
        if (!securities || (securities && securities.length <= 0)) return
        return (
            <select>
                {securities.map((s, i) => {
                    return (
                        <option value={s} key={i}>{s}</option>
                    )
                })}
            </select>
        )
    }

    const renderSearchSpace = () => {
        if (!searchResults || (searchResults && searchResults.length <= 0)) {
            return
        }

        return (
            <div className="search-space">
                <table>
                    <tr>
                        {ROW_SCHEMA.map((r, i) => {
                            if (r === "Security ID") {
                                return <th key={i} className="extra-left-pad">{r}</th>
                            }

                            return (
                                <th key={i}>{r}</th>
                            )
                        })}
                    </tr>
                    <tbody>
                        {searchResults.map((s, i) => <SearchResult key={i} {...s} />)}
                    </tbody>
                </table>
            </div>
        )
    }

    // Dynamically changing styles as actions are performed in
    // the query
    let uploadCSVButtonStyles = "file-input-container"
    if (file) uploadCSVButtonStyles += " uploaded"

    let uploadCSVButtonLabel = "Upload CSV"
    if (file) uploadCSVButtonLabel = "CSV Uploaded!"

    return (
        <div className="search-container">
            <div className="search m-auto">
                <div className="left-sidebar">
                    <div className="csv-form">
                        <button className={uploadCSVButtonStyles}>
                            <p>{uploadCSVButtonLabel}</p>
                            <input
                                type={"file"}
                                accept={".csv"}
                                onChange={handleFileChange}
                            />
                        </button>
                        <button onClick={e => handleFileImport(e)}>
                            Import CSV
                        </button>
                    </div>
                    <div className="query-area">
                        {renderSecuritiesDropdown()}
                        <input
                            type={"text"}
                            value={query}
                            onChange={handleQueryChange}
                            placeholder={"Search for securities or street IDs"}
                        />
                        <button onClick={handleSearch}>Search</button>
                    </div>
                </div>
                {renderSearchSpace()}
            </div>
        </div>
    );
}

export default Search