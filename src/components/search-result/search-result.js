import React from 'react'

import './search-result.css'

const ROW_SCHEMA = [
    "security_id",
    "cusip",
    "sedol",
    "isin",
    "ric",
    "bloomberg",
    "bbg",
    "symbol",
    "root_symbol",
    "bb_yellow",
    "spn"
]

class SearchResult extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            ...props
        }
    }

    render() {
        return (
            <tr className="search-result">
                {ROW_SCHEMA.map((r, i) => {
                    // Displaying empty cells
                    if (this.state.content[r] === "") {
                        return (
                            <td key={i} className="empty-cell">
                                <div>Nothing</div>
                            </td>
                        )
                    }

                    // Making the cells where the matches
                    // were found flash
                    let cellStyles = ""
                    if (
                        this.state.content[r] === this.state.placeWhereMatchWasFound &&
                        this.state.priority == 1) {
                        cellStyles = " flash-full-match"
                    }

                    if (
                        this.state.content[r] === this.state.placeWhereMatchWasFound &&
                        this.state.priority == 2
                    ) {
                        cellStyles = " flash-partial-match"
                    }

                    return (
                        <td key={i} className={cellStyles}>
                            {this.state.content[r]}
                        </td>
                    )
                })}
            </tr>
        )
    }
}

export default SearchResult