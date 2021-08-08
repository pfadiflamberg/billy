import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { clearErrors, selectErrors, BillyError } from "./errorSlice";
import { Modal, ListGroup } from 'react-bootstrap';

export function ErrorView() {

    const dispatch = useAppDispatch();
    const errors = useAppSelector(selectErrors);

    let hasErrors = 0 < errors.length;

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
                            {errors[0].details && errors[0].details.map((err: BillyError) => {
                                return (
                                    <ListGroup.Item>{err.description + " "}
                                        {err.link &&
                                            <a target="_blank" rel="noreferrer" href={err.link}>view</a>
                                        }
                                    </ListGroup.Item>)
                            })}
                        </ListGroup>
                    </Modal.Body>
                </div>
            }
        </Modal>
    )

}