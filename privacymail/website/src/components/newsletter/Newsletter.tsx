import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";

const Newsletter = () => {
    let { id } = useParams();
    const [newsletter, setNewsletter] = useState<INewsletter>();
    useEffect(() => getNewsletter(id, setNewsletter), []);

    console.log(newsletter);



    return <div><FaqHint /></div>
}
export default Newsletter