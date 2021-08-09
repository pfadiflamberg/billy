import { useAppDispatch } from "../../app/hooks";
import { Button } from 'react-bootstrap';
import { Payment, uploadPayments } from "./paymentSlice";

import { useRef } from 'react'

export function PaymentsUploadButton() {

    const dispatch = useAppDispatch();

    const inputRef = useRef<HTMLInputElement>(null);

    const handleUpload = () => {
        inputRef.current?.click();
    };

    const handleFiles = () => {
        var list = inputRef.current?.files;
        if (list == undefined) {
            throw 'FileList undefined'
        }
        var reader = new FileReader();
        for (let i = 0; i < list.length; i++) {
            var file = list.item(i);
            if (file == undefined) {
                throw 'File undefined'
            }
            reader.addEventListener('load', function (e) {
                var payments: Payment[] = [];
                var content = e.target?.result;
                if (content instanceof ArrayBuffer) {
                    throw 'Unexpected Type'
                }
                content?.split('\n').forEach(l => {
                    var values: RegExpMatchArray[] = [];
                    [/([0-9]{10,})/, // match esr
                        /,\s*([0-9]+\.[0-9]{2})\s*,/, // match amount
                        /([0-9]{2})\.([0-9]{2})\.([0-9]{4})/ // match date
                    ].forEach(r => {
                        var match = l.match(r);
                        if (match === null) {
                            return;
                        }
                        values.push(match); // capture group
                    })
                    if (values.length < 3) {
                        return;
                    }
                    payments.push({
                        esr: values[0][1],
                        amount: values[1][1],
                        date: new Date([values[2][2], values[2][1], values[2][3]].join("/")).toISOString()
                    })
                });
                console.log(payments);
                dispatch(uploadPayments(payments));
            });
            reader.readAsBinaryString(file);
        }
    };

    return (
        <div>
            <input ref={inputRef} className="d-none" type="file" accept=".csv" onChange={handleFiles} />
            <Button onClick={handleUpload}>
                Upload Payments
            </Button>
        </div>
    )
}