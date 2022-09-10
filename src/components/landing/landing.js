import React from 'react'

import './landing.css'

class Landing extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            fadeOutLanding: null
        }

        this.startEngine = this.startEngine.bind(this)
    }

    startEngine() {
        this.setState({ fadeOutLanding: true })

        // Timeout for the same duration as the animation
        // so that the component is unmounted only
        // after the animation completes
        setTimeout(() => {
            this.props.startEngine()
        }, 2000)
    }

    render() {

        let landingStyles = "landing"
        if (this.state.fadeOutLanding) {
            landingStyles += " fadeOut"
        }

        return (
            <div className={landingStyles}>
                <h1>Welcome to Pegasus</h1>
                <p>A mythical search engine for all your needs - investments, web3, filtering, and much more</p>
                <button onClick={this.startEngine}>Start searching</button>
            </div>
        )
    }
}

export default Landing