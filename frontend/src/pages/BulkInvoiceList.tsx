import {useAppSelector, useAppDispatch} from "../app/hooks";
import {selectBulks} from "../features/bulk/bulkSlice";
import {selectBulk, duplicateBulk} from "../features/bulk/bulkSlice";
import {ListGroup, Badge, DropdownButton, Dropdown} from 'react-bootstrap';

function badgeVariantForStatus(status: string): string {
    switch (status) {
        case 'created':
            return 'secondary'
        case 'issued':
            return 'primary'
        case 'closed':
            return 'dark'
        default:
            return 'warning'
    }
}

export function BulkInvoiceList() {

    const dispatch = useAppDispatch();

    const bulks = useAppSelector(selectBulks);

    return (
        <div className="BulkInvoiceList">
            <ListGroup>
                { Object.keys(bulks).reverse().map((name) => {
                    const bulk = bulks[name];
                    return (
                        <ListGroup.Item key={name} action onClick={() => dispatch(selectBulk(name))}>
                            {bulk.display_name}
                            <div>
                            <Badge variant={badgeVariantForStatus(bulk.status)}>{bulk.status}</Badge>
                            <DropdownButton title={''} onClick={e => e.stopPropagation()}>
                                <Dropdown.Item onClick={e => dispatch(duplicateBulk(bulk))}>Duplicate</Dropdown.Item>
                            </DropdownButton>
                            </div>
                        </ListGroup.Item>
                    )
                }) }
            </ListGroup>
        </div>
    )
}