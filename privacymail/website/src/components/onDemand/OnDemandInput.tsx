import React from "react";

interface OnDemandInputProps {
    rawEmail: string;
    setRawEmail: (email: string) => void;
    runAnalysis: () => void;
}

const OnDemandInput = (props: OnDemandInputProps) => {
    return (
        <div>
            <textarea
                id="text"
                value={props.rawEmail}
                placeholder="Hier Raw-Email eingeben"
                onChange={e => props.setRawEmail(e.target.value)}
                rows={20}
            />

            <button
                onClick={e => {
                    props.runAnalysis();
                }}
            >
                Send
            </button>
        </div>
    );
};

export default OnDemandInput;
