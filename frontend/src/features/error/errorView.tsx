import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { clearErrors, selectErrors, BillyError } from "./errorSlice";
import { Modal, ListGroup } from 'react-bootstrap';

export function ErrorView() {

    const dispatch = useAppDispatch();
    const errors = useAppSelector(selectErrors);

    let hasErrors = 0 < errors.length;

    if (errors[0]) {
        console.log(errors[0].details);
    }

    return (
        <Modal show={hasErrors} onHide={() => dispatch(clearErrors())}>
            {hasErrors &&
                <div>
                    <Modal.Header closeButton>
                        <Modal.Title>{errors[0].title}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {errors[0].description}
                        <ListGroup>
                            {errors[0].details.map((err: BillyError) => {
                                return <ListGroup.Item>{err.description} <a target="_blank" href={err.link}>view</a></ListGroup.Item>
                            })}
                        </ListGroup>
                    </Modal.Body>
                </div>
            }
        </Modal>
    )

}