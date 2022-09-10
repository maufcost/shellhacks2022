import React from 'react'

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
                    if (this.state.content[r] === "") {
                        return (
                            <td key={i} className="empty-cell">
                                <div>Nothing</div>
                            </td>
                        )
                    }
                    return (
                        <td key={i}>{this.state.content[r]}</td>
                    )
                })}
            </tr>
        )
    }
}

export default SearchResult