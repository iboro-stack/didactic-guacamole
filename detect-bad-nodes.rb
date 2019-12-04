require 'json'

MACCOUNTS = { }
MACMAX = [0]

def process_doc(doc)
  kvtodo = [ ]
  mac = doc['ip']
  mccmd = doc['mccmd']
  return if mccmd != 'get_system_info'
  return unless mac
  curcount = MACCOUNTS[mac] || 0
  curcount += 1
  MACCOUNTS[mac] = curcount
  if curcount > MACMAX[0]
    MACMAX[0] = curcount
  end
end

def check_bad()
  badmacs = { }
  MACCOUNTS.each do |k, v|
    if v < MACMAX[0] - 3
      badmacs[k] = MACMAX[0] - v
    end
  end
  tosort = [ ]
  badmacs.keys.each do |k, v|
    tosort << [k, v]
  end
  badmacs = badmacs.sort { |a,b| a[1] <=> b[1] }
  badmacs.each do |mac, behind|
    puts "IP: #{mac}  BEHIND: #{behind}"
  end
end

lineno = 0
t0 = Time.now.to_f
while line = gets
  lineno += 1
  if lineno % 1000 == 0
    dt = Time.now.to_f - t0
    linesPerSec = (lineno / dt).to_i
    puts "Processed #{lineno} events. Processing rate #{linesPerSec} ev/s"
  end
  begin
    obj = JSON.parse(line)
    process_doc(obj)
  rescue JSON::ParserError
  end
end
check_bad()
exit(0)
