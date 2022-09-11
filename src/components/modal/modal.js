import React from 'react'

import './modal.css'

const Modal = () => {
    const handleUploadNewRule = () => {

    }

    const handleSubmit = () => {

    }

    return (
        <div className="modal-container">
            <div className="modal">
                <header>
                    <p className="title">Modify your organization's rule set</p>
                    <button>Cancel</button>
                </header>
                <div className="manny">
                    <div className="lefty">
                        <div className="row">
                            <button onClick={handleUploadNewRule}>Upload New Rule</button>
                            <button onClick={handleSubmit}>Submit</button>
                        </div>
                        <div className="row">
                            <input type="text" placeholder="Search for pre-made rules" />
                            <button onClick={handleUploadNewRule}>Search</button>
                        </div>
                    </div>
                    <div className="righty">
                        <p className="title">Your organization's custom rule set</p>
                        <div>
                            
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Modal