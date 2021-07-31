import { useAppSelector, useAppDispatch } from "../app/hooks";
import { selectBulks } from "../features/bulk/bulkSlice";
import { selectBulk, duplicateBulk, getBulkPDFs } from "../features/bulk/bulkSlice";
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
                        <ListGroup.Item key={name} action onClick={() => dispatch(selectBulk(bulk))}>
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
                                                    <Dropdown.Item onClick={e => dispatch(selectBulk(bulk))}>Issue</Dropdown.Item>
                                                }
                                                <Dropdown.Item onClick={e => console.log('TODO')}>TODO: Send via Email</Dropdown.Item>
                                                <Dropdown.Item onClick={e => dispatch(getBulkPDFs(bulk))}>Download PDFs</Dropdown.Item>
                                                <Dropdown.Item onClick={e => console.log('TODO')}>TODO: Upload Payment Record</Dropdown.Item>
                                                <Dropdown.Divider />
                                                <Dropdown.Item onClick={e => dispatch(selectBulk(bulk))}>View</Dropdown.Item>
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