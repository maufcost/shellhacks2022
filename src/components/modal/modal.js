import React, { useState } from 'react'

// Assets
import IconCheck from '../../assets/icon-check.png'

// Stylings
import './modal.css'

// Sub-components
import FolderTree, { testData } from 'react-folder-tree';
import 'react-folder-tree/dist/style.css';

const Modal = props => {
    const [file, setFile] = useState(null)
    const [rules, setRules] = useState([])
    const [ruleString, setRuleString] = useState("")
    const [ruleIPFS, setIpfsRule] = useState("")

    const fileReader = new FileReader()

    const ruleTree = {
        name: 'Custom Rules',
        checked: 0.5,   // half check: some children are checked
        isOpen: true,   // this folder is opened, we can see it's children
        children: [
            {
                name: 'Python 3', checked: 1,
                children: [
                    {
                        name: 'Code Injection',
                        checked: 0.5,
                        isOpen: true,
                    },
                    {
                        name: 'Flask',
                        checked: 0.5,
                        isOpen: true,
                        children: [{ name: 'SSTI', checked: 0 },],
                    },
                ]
            },
            {
                name: 'Javascript',
                children: [
                    {
                        name: 'Insecure Deserialization',
                        checked: 1,
                        isOpen: true
                    }
                ]
            }
        ],
    }

    const handleFileChange = e => {
        if (!e) return

        const file = e.target.files[0]

        setFile(file)
        handleUploadNewRule(file)
    }

    const handleUploadNewRule = f => {
        if (f) {
            fileReader.onload = event => {
                const output = event.target.result
                setRuleString(output)
                const bytes = new TextEncoder().encode(output)
                fetch("/upload-rule", {
                    method: "POST",
                    body: bytes
                })
                .then( async response => {
                    let data = await response.json();
                    console.log(data);
                    setIpfsRule(data.value.url);
                    alert("Rule uploaded successfully!");
                    alert(data.value.url);
                });
            };

            // Reads source code as a regular string.
            fileReader.readAsText(f)
        }
    }

    const handleSubmit = () => {
        setIpfsRule("Uploading to ipfs...");
    }

    const handleSearch = () => {
        setRules([
            "Python SQLi - Microsoft (verified)",
            "SQL Injection (Flask) - Google (verified)",
            "Python3 SQLi MongoDB - Random User"
        ])
    }

    // Dynamically changing styles as actions are performed in
    // the query

    // Upload new rule button
    let uploadRuleStyles = "file-input-container"
    if (file) uploadRuleStyles += " uploaded"

    let uploadRuleButtonLabel = "Upload New Rule"
    if (file) uploadRuleButtonLabel = "New Rule Uploaded!"

    return (
        <div className="modal-container">
            <div className="modal">
                <header>
                    <p className="title">Modify your organization's rule set</p>
                    <button onClick={props.closeModal}>Cancel</button>
                </header>
                <div className="manny">
                    <div className="lefty">
                        <div className="row">
                            <button className={uploadRuleStyles}>
                                <p>{uploadRuleButtonLabel}</p>
                                <input
                                    type={"file"}
                                    accept={".py,.js,.c,.cpp,.java"}
                                    onChange={handleFileChange}
                                />
                            </button>
                            <button onClick={handleSubmit}>Submit <img src={IconCheck} /></button>
                        </div>
                        <div className="row">
                            <input type="text" placeholder="Search for pre-made rules" />
                            <button onClick={handleSearch}>Search</button>
                        </div>
                        <div className="rule-results">
                            {rules.map((r, i) => {
                                return (
                                    <div className="rule-result" key={i}>
                                        <p>{r}</p>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                    <div className="righty">
                        <p className="title">Your organization's custom rule set</p>
                        <div>
                            <FolderTree
                                data={ruleTree}
                                initCheckedStatus='custom'  // default: 0 [unchecked]
                                initOpenStatus='custom'     // default: 'open'
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Modal