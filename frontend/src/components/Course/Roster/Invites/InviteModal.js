import React, {useState} from 'react';
import { Modal, Button } from 'semantic-ui-react';
import AddForm from './AddForm';
import {gql} from "apollo-boost";
import {useMutation} from "@apollo/react-hooks";
import Alert from "@material-ui/lab/Alert";
import Snackbar from "@material-ui/core/Snackbar";

const INVITE_OR_ADD_EMAILS = gql`
  mutation InviteOrAddEmails($input: InviteOrAddEmailsInput!) {
    inviteOrAddEmails(input: $input) {
      invitedCourseUsers {
        email
      }
      addedCourseUsers {
        user {
          fullName
          email
        }
      }
      existingInvitedCourseUsers {
        email
      }
      existingCourseUsers {
        user {
          fullName
          email
        }
      }
    }
  }
`;

const InviteModal = (props) => {
  const [inviteOrAddEmails, { loading }] = useMutation(INVITE_OR_ADD_EMAILS);
  const [input, setInput] = useState({ emails: [], kind: null });
  const [error, setError] = useState(null);
  const [disabled, setDisabled] = useState(true);

  const handleInputChange = (e, { name, value }) => {
    input[name] = value;
    setInput(input);
    setDisabled(input.emails.length === 0 || input.kind === null)
  };

  const inviteFunc = async () => {
    if (input.emails.length === 0 || input.kind === null) {
      return
    }
    try {
      await inviteOrAddEmails({
        variables: {
          input: {
            emails: input.emails,
            kind: input.kind,
            courseId: props.courseId,
          }
        }
      });
      props.closeFunc();
      props.successFunc();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <Modal open={ props.open }>
      <Modal.Header>Invite User</Modal.Header>
      <Modal.Content>
        <AddForm users={ props.users } courseId={ props.courseId } changeFunc={ handleInputChange }/>
      </Modal.Content>
      <Modal.Actions>
        <Button
          content='Invite'
          color='blue'
          disabled={loading || disabled}
          loading={loading}
          onClick={ inviteFunc }/>
        <Button
          content='Cancel'
          disabled={loading}
          onClick={ props.closeFunc }/>
      </Modal.Actions>
      <Snackbar open={ error } autoHideDuration={6000} onClose={ () => setError(null) }>
        <Alert severity={ 'error' } onClose={ () => setError(null) }>
          <span>
            {
              error && error.includes('Course cannot have more than') ? 'Course cannot have more than 1000 users' : error
            }
          </span>
        </Alert>
      </Snackbar>
    </Modal>
  )
};

export default InviteModal;
