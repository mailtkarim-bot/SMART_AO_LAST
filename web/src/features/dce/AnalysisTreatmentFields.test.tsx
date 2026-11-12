import {fireEvent,render,screen} from "@testing-library/react";
import {expect,it} from "vitest";
import {useState} from "react";
import {AnalysisTreatmentFields,emptyTreatment} from "./AnalysisTreatmentFields";
it("preserves local wall-clock due time while storing an unambiguous instant",()=>{
 function Harness(){const [v,set]=useState(emptyTreatment("TECHNICAL"));return <AnalysisTreatmentFields id="test" value={v} onChange={set}/>;}
 render(<Harness/>);const input=screen.getByLabelText(/Échéance — vide/);
 fireEvent.change(input,{target:{value:"2026-10-23T10:00"}});expect(input).toHaveValue("2026-10-23T10:00");
 fireEvent.change(input,{target:{value:"2026-10-23T10:30"}});expect(input).toHaveValue("2026-10-23T10:30");
});
it("records explicit hypotheses while missing input remains unknown",()=>{
 function Harness(){const [v,set]=useState(emptyTreatment("TECHNICAL"));return <AnalysisTreatmentFields id="hyp" value={v} onChange={set}/>;}
 render(<Harness/>);const input=screen.getByLabelText(/Hypothèses déclarées/);
 expect(input).toHaveValue("");fireEvent.change(input,{target:{value:"Deux rotations de livraison"}});expect(input).toHaveValue("Deux rotations de livraison");
});
