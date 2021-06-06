import {useAppSelector} from "../app/hooks";
import {selectBulks} from "../features/bulk/bulkSlice";
import {Card} from 'react-bootstrap';

export function BulkInvoiceList() {

    const bulks = useAppSelector(selectBulks);

    return (
        <div className="BulkInvoiceList">
            { Object.keys(bulks).reverse().map((name) => {
                const bulk = bulks[name];
                console.log(bulk);
                return (
                    <Card key={name}>
                        <Card.Body>
                            <Card.Title>{bulk.display_name}</Card.Title>
                        </Card.Body>
                    </Card> // TODO: onclick view order

                )
            }) }
        </div>
    )
}