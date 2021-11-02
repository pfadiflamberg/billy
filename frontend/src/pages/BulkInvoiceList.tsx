import { useAppSelector, useAppDispatch } from "../app/hooks";
import { selectBulks, viewPDFs } from "../features/bulk/bulkSlice";
import { duplicateBulk } from "../features/bulk/bulkSlice";
import { ListGroup, Dropdown, Row, Col, ButtonGroup, Button, DropdownButton } from 'react-bootstrap';

function badgeVariantForStatus(status: string): string {
    switch (status) {
        case 'draft':
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
                {Object.keys(bulks).reverse().map((name) => {
                    const bulk = bulks[name];
                    return (
                        <ListGroup.Item key={name} action onClick={() => window.open(bulk.name, "_self")}>
                            <Row>
                                <Col>
                                    <div className="BulkInvoiceListTitle">
                                        {bulk.title}
                                    </div>
                                    <div className="BulkInvoiceListSubTitle">
                                        updated: {new Date(bulk.update_time).toLocaleString('de-DE')}
                                    </div>
                                </Col>
                                <Col xs={3}>
                                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                        <ButtonGroup size="sm">
                                            <Button
                                                onClick={e => e.stopPropagation()}
                                                variant={badgeVariantForStatus(bulk.status)}>
                                                {bulk.status}
                                            </Button>
                                            <DropdownButton
                                                as={ButtonGroup}
                                                title={''}
                                                id={bulk.name}
                                                size="sm"
                                                variant={badgeVariantForStatus(bulk.status)}
                                                onClick={e => e.stopPropagation()}
                                            >
                                                {bulk.status === 'draft' &&
                                                    <Dropdown.Item onClick={e => window.open(bulk.name, "_self")}>Issue</Dropdown.Item>
                                                }
                                                {bulk.status === 'issued' &&
                                                    <div>
                                                        <Dropdown.Item onClick={e => dispatch(viewPDFs(bulk))}>Pending invoices as PDF</Dropdown.Item>
                                                        <Dropdown.Item onClick={e => window.open(bulk.name, "_self")}>Send as Email</Dropdown.Item>
                                                    </div>
                                                }
                                                <Dropdown.Divider />
                                                <Dropdown.Item onClick={e => window.open(bulk.name, "_self")}>View</Dropdown.Item>
                                                <Dropdown.Item onClick={e => dispatch(duplicateBulk(bulk))}>Duplicate</Dropdown.Item>
                                            </DropdownButton>
                                        </ButtonGroup>
                                    </div>
                                </Col>
                            </Row>
                        </ListGroup.Item>
                    )
                })}
            </ListGroup>
        </div>
    )
}