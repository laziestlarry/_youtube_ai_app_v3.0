import './alexandria.css';
import ProtocolApp from '@/components/alexandria/ProtocolApp';

export const metadata = {
  title: 'The Alexandria Protocol',
  description: 'Archive intelligence and value generation system for revenue opportunities.',
};

export default function AlexandriaPage() {
  return (
    <div className="alexandria-shell min-h-screen">
      <ProtocolApp />
    </div>
  );
}
